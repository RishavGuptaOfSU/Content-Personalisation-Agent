"""Feedback loop: store the signal, learn from it, and adapt — carefully.

Guard rail from the spec: a *single* feedback event never rewrites the profile.
A feedback comment becomes a long-term memory immediately (so the next request
already benefits from it), but a structural profile change only happens once the
same signal has been seen ``FEEDBACK_PROMOTION_THRESHOLD`` times.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.catalog import agent_exists, get_agent_spec
from app.core.config import settings
from app.core.logging import get_logger
from app.memory.service import get_memory_service
from app.models.conversation import Message
from app.models.feedback import Feedback
from app.models.memory import Memory
from app.services.profile_service import get_profile_service

logger = get_logger(__name__)


@dataclass(slots=True)
class FeedbackOutcome:
    feedback: Feedback
    memories_created: list[str] = field(default_factory=list)
    memories_reinforced: list[str] = field(default_factory=list)
    profile_changes: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    @property
    def profile_updated(self) -> bool:
        return bool(self.profile_changes)


#: Signal -> (global value, per-agent overrides keyed by agent_key)
_LENGTH_SIGNALS: tuple[tuple[re.Pattern[str], str, dict[str, tuple[str, str]]], ...] = (
    (
        re.compile(r"\b(concise|shorter|short|brief|briefer|less verbose|too long|tighter)\b", re.I),
        "concise",
        {
            "marketing.social-copy": ("length", "Very short (<50 words)"),
            "creative.story-writer": ("length", "Micro (<150 words)"),
            "research.summarizer": ("length", "One paragraph"),
        },
    ),
    (
        re.compile(r"\b(more detail|detailed|longer|expand|too short|elaborate|in.?depth)\b", re.I),
        "detailed",
        {
            "marketing.social-copy": ("length", "Medium (120-250)"),
            "creative.story-writer": ("length", "Short (500-1500)"),
            "research.summarizer": ("length", "Detailed"),
        },
    ),
)

_STYLE_SIGNALS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(more direct|blunt|no fluff|get to the point|cut the)\b", re.I), "direct"),
    (re.compile(r"\b(more formal|professional|business tone)\b", re.I), "professional"),
    (re.compile(r"\b(friendlier|warmer|less formal|casual)\b", re.I), "casual"),
    (re.compile(r"\b(academic|rigorous|cite)\b", re.I), "academic"),
)

_SKILL_SIGNALS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(too basic|too simple|more advanced|deeper technical)\b", re.I), "advanced"),
    (re.compile(r"\b(too advanced|too complex|simpler|easier|confusing)\b", re.I), "beginner"),
)


class FeedbackService:
    def __init__(self) -> None:
        self._memory = get_memory_service()
        self._profiles = get_profile_service()

    # ------------------------------------------------------------------ api
    def submit(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        message: Message,
        rating: int,
        feedback_text: str | None,
    ) -> FeedbackOutcome:
        agent_key = message.agent_key
        if not agent_key or not agent_exists(agent_key):
            raise ValueError("This message was not produced by a known agent.")
        spec = get_agent_spec(agent_key)

        feedback = Feedback(
            user_id=user_id,
            agent_key=spec.key,
            domain=spec.domain,
            message_id=message.id,
            conversation_id=message.conversation_id,
            rating=1 if rating > 0 else -1,
            feedback_text=(feedback_text or "").strip() or None,
        )
        db.add(feedback)
        db.flush()

        outcome = self.process(db, user_id=user_id, feedback=feedback)

        feedback.processed = True
        feedback.outcome = {
            "memories_created": outcome.memories_created,
            "memories_reinforced": outcome.memories_reinforced,
            "profile_changes": outcome.profile_changes,
        }
        db.commit()
        db.refresh(feedback)
        outcome.feedback = feedback
        return outcome

    def process(
        self, db: Session, *, user_id: uuid.UUID, feedback: Feedback
    ) -> FeedbackOutcome:
        """The ``process_feedback`` step of the pipeline."""
        outcome = FeedbackOutcome(feedback=feedback)
        text = (feedback.feedback_text or "").strip()

        if text:
            from app.memory.extractor import get_memory_extractor

            candidates = get_memory_extractor().from_feedback(text, feedback.rating)
            for candidate in candidates:
                try:
                    memory, created = self._memory.remember(
                        db,
                        user_id=user_id,
                        candidate=candidate,
                        agent_key=feedback.agent_key,
                        domain=feedback.domain,
                        conversation_id=feedback.conversation_id,
                        extra_meta={
                            "origin": "feedback",
                            "feedback_id": str(feedback.id),
                            "rating": feedback.rating,
                        },
                    )
                except ValueError:
                    continue
                if created:
                    outcome.memories_created.append(memory.content)
                else:
                    outcome.memories_reinforced.append(memory.content)

            self._maybe_adapt_profiles(db, user_id=user_id, feedback=feedback, outcome=outcome)

        if feedback.rating < 0 and not text:
            # A bare thumbs-down is a weak signal: recorded for aggregate
            # analysis, never acted on directly.
            outcome.message = (
                "Thanks — recorded. Tell us what to change and the agent will adapt."
            )
        elif outcome.profile_changes:
            outcome.message = "Preference learned and your profile was updated."
        elif outcome.memories_created or outcome.memories_reinforced:
            outcome.message = "Preference saved — future responses will use it."
        else:
            outcome.message = "Thanks for the feedback."

        return outcome

    # -------------------------------------------------------------- private
    def _maybe_adapt_profiles(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        feedback: Feedback,
        outcome: FeedbackOutcome,
    ) -> None:
        text = feedback.feedback_text or ""
        threshold = settings.FEEDBACK_PROMOTION_THRESHOLD

        # --- response length -------------------------------------------------
        for pattern, target_value, agent_overrides in _LENGTH_SIGNALS:
            if not pattern.search(text):
                continue
            observations = self._signal_strength(db, user_id, pattern, feedback.agent_key)
            if observations < threshold:
                logger.info(
                    "Length signal %r seen %d/%d times — not adapting the profile yet",
                    target_value,
                    observations,
                    threshold,
                )
                continue
            if self._profiles.apply_learned_global_preference(
                db, user_id, "preferred_response_length", target_value
            ):
                outcome.profile_changes["global.preferred_response_length"] = target_value

            override = agent_overrides.get(feedback.agent_key)
            if override:
                field_key, value = override
                profile = self._profiles.get_agent_profile(db, user_id, feedback.agent_key)
                if profile is not None and self._profiles.apply_learned_agent_preference(
                    db, profile, field_key, value
                ):
                    outcome.profile_changes[f"{feedback.agent_key}.{field_key}"] = value
            break

        # --- communication style ---------------------------------------------
        for pattern, style in _STYLE_SIGNALS:
            if not pattern.search(text):
                continue
            if self._signal_strength(db, user_id, pattern, feedback.agent_key) < threshold:
                continue
            if self._profiles.apply_learned_global_preference(
                db, user_id, "communication_style", style
            ):
                outcome.profile_changes["global.communication_style"] = style
            break

        # --- skill level ------------------------------------------------------
        for pattern, level in _SKILL_SIGNALS:
            if not pattern.search(text):
                continue
            if self._signal_strength(db, user_id, pattern, feedback.agent_key) < threshold:
                continue
            if self._profiles.apply_learned_global_preference(
                db, user_id, "general_skill_level", level
            ):
                outcome.profile_changes["global.general_skill_level"] = level
            profile = self._profiles.get_agent_profile(db, user_id, feedback.agent_key)
            if profile is not None and self._profiles.apply_learned_agent_preference(
                db, profile, "level", level.capitalize()
            ):
                outcome.profile_changes[f"{feedback.agent_key}.level"] = level.capitalize()
            break

        if outcome.profile_changes:
            db.flush()

    @staticmethod
    def _signal_strength(
        db: Session, user_id: uuid.UUID, pattern: re.Pattern[str], agent_key: str
    ) -> int:
        """How many times has this signal been observed for this user?

        Counts both matching feedback comments and the reinforcement counter on
        stored memories, so "I keep asking for shorter posts" is what triggers a
        profile change — not one click.
        """
        comments = db.scalars(
            select(Feedback.feedback_text).where(
                Feedback.user_id == user_id, Feedback.feedback_text.is_not(None)
            )
        ).all()
        count = sum(1 for comment in comments if comment and pattern.search(comment))

        memory_occurrences = db.scalar(
            select(func.coalesce(func.sum(Memory.occurrences), 0)).where(
                Memory.user_id == user_id,
                Memory.agent_key == agent_key,
                Memory.kind.in_(("preference", "feedback")),
            )
        )
        reinforced = 0
        memories = db.scalars(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.kind.in_(("preference", "feedback")),
            )
        ).all()
        for memory in memories:
            if pattern.search(memory.content):
                reinforced = max(reinforced, memory.occurrences)

        logger.debug(
            "Signal strength: comments=%d reinforced=%d (sum=%s)",
            count,
            reinforced,
            memory_occurrences,
        )
        return max(count, reinforced)

    # ----------------------------------------------------------------- stats
    def counts(self, db: Session, user_id: uuid.UUID) -> tuple[int, int]:
        rows = db.execute(
            select(Feedback.rating, func.count(Feedback.id))
            .where(Feedback.user_id == user_id)
            .group_by(Feedback.rating)
        ).all()
        helpful = 0
        unhelpful = 0
        for rating, count in rows:
            if int(rating) > 0:
                helpful += int(count)
            else:
                unhelpful += int(count)
        return helpful, unhelpful

    def list_for_user(
        self,
        db: Session,
        user_id: uuid.UUID,
        *,
        agent_key: str | None = None,
        domain: str | None = None,
        limit: int = 50,
    ) -> list[Feedback]:
        statement = select(Feedback).where(Feedback.user_id == user_id)
        if agent_key:
            statement = statement.where(Feedback.agent_key == agent_key)
        if domain:
            statement = statement.where(Feedback.domain == domain)
        statement = statement.order_by(Feedback.created_at.desc()).limit(min(limit, 200))
        return list(db.scalars(statement).all())


_service: FeedbackService | None = None


def get_feedback_service() -> FeedbackService:
    global _service
    if _service is None:
        _service = FeedbackService()
    return _service
