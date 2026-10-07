"""Local development LLM provider.

Purpose: let the *entire* stack (routing, personalization, memory, feedback,
persistence, UI) be exercised end to end without AWS credentials.

It is **not** a fake wired into the product path: it is a provider
implementation selected by ``LLM_PROVIDER=mock``. It composes its answer
deterministically from the same personalization payload a real model receives,
so the demo visibly proves that the profile + memory pipeline reaches the
generation step. Every response it produces is tagged ``provider="local-dev"``
in the message metadata and the UI renders a badge for it.

Set ``LLM_PROVIDER=bedrock`` and the identical call sites hit AWS Bedrock.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from app.llm.base import BaseLLMProvider, ChatMessage, LLMResponse

_STOPWORDS = {
    "a", "an", "the", "about", "for", "of", "on", "in", "to", "me", "my", "please",
    "can", "you", "could", "would", "write", "create", "make", "give", "explain",
    "generate", "draft", "help", "i", "want", "need", "with", "some", "how", "do",
    "what", "is", "are", "and", "or", "using", "use", "that", "this", "it",
}

_LENGTH_PLAN = {
    "concise": {"bullets": 3, "sections": 2, "words": "~120 words"},
    "balanced": {"bullets": 4, "sections": 3, "words": "~250 words"},
    "detailed": {"bullets": 6, "sections": 4, "words": "~450 words"},
}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _first(value: Any, fallback: str = "") -> str:
    items = _as_list(value)
    return items[0] if items else fallback


def _join(values: Any, fallback: str = "your stack", limit: int = 4) -> str:
    items = _as_list(values)[:limit]
    if not items:
        return fallback
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


#: Artefact nouns that wrap the real subject ("write a LinkedIn *post about* X").
_ARTEFACT_RE = re.compile(
    r"^(?:a|an|the|another|some)?\s*"
    r"(?:linkedin|instagram|twitter|x|facebook|youtube|blog|email|short|long|quick|brief)?\s*"
    r"(?:post|posts|caption|tweet|thread|article|story|script|poem|essay|summary|"
    r"report|newsletter|ad|copy|quiz|plan|guide|note)\s+"
    r"(?:about|on|for|covering|regarding)\s+",
    re.IGNORECASE,
)


def _sentence_case(text: str) -> str:
    """Upper-case the first letter only — preserves acronyms like AI, SQL, RAG."""
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def _topic(request: str) -> str:
    """Best-effort subject extraction from the user's request."""
    text = request.strip().rstrip("?.!")
    text = re.sub(r"^(please\s+)?(can|could|would)\s+you\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"^(please\s+)?(explain|write|create|make|generate|draft|give me|help me with|"
        r"tell me about|summarize|summarise|analyze|analyse|improve|review|build|"
        r"come up with|brainstorm|research|look up|"
        r"find (?:information|info|details|out)?\s*(?:about|on)?)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    # "a LinkedIn post about AI automation" -> "AI automation"
    stripped = _ARTEFACT_RE.sub("", text)
    if stripped.strip():
        text = stripped
    text = re.sub(r"^(a|an|the|me|my|some|another)\s+", "", text, flags=re.IGNORECASE)
    # Drop trailing audience qualifiers: the agent profile already encodes them.
    text = re.sub(
        r"\s+for\s+(class\s+\d+|grade\s+\d+|beginners?|kids|students|"
        r"a\s+\w+\s+role|my\s+\w+)\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = " ".join(text.split())
    return text[:160] or request[:160]


def _keywords(request: str, limit: int = 6) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", request.lower())
    seen: list[str] = []
    for word in words:
        if word in _STOPWORDS or word in seen:
            continue
        seen.append(word)
        if len(seen) >= limit:
            break
    return seen


def _extract_pairs(text: str) -> tuple[list[str], list[float]]:
    """Pull "Label 123" / "Label: 123" pairs out of a message."""
    pairs = re.findall(r"([A-Za-z][A-Za-z ._-]{0,24}?)\s*[:=]?\s*(-?\d[\d,]*\.?\d*)", text)
    labels: list[str] = []
    values: list[float] = []
    for label, number in pairs:
        cleaned = label.strip(" .:-")
        if not cleaned or cleaned.lower() in ("chart", "plot", "graph", "this"):
            continue
        try:
            values.append(float(number.replace(",", "")))
        except ValueError:
            continue
        labels.append(cleaned[:24])
    return labels[:12], values[:12]


def _bullet_block(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items if item)


class LocalDevLLMProvider(BaseLLMProvider):
    """Deterministic, personalization-aware provider for local development."""

    name = "local-dev"

    @property
    def default_model(self) -> str:
        return "local-dev-composer-v1"

    # ------------------------------------------------------------------ api
    def generate(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
        hints: dict[str, Any] | None = None,
    ) -> LLMResponse:
        hints = hints or {}
        request = hints.get("request") or self._last_user_message(messages)
        # Composers are domain-shaped; an agent key is "<domain>.<slug>".
        agent_type = str(hints.get("domain") or hints.get("agent_type") or "research")
        if "." in agent_type:
            agent_type = agent_type.split(".", 1)[0]

        # Visual agents expect a JSON design/chart spec, not prose.
        output_kind = str(hints.get("output_kind") or "text")
        if output_kind in ("image", "chart"):
            return self._compose_media_spec(output_kind, request, hints)
        global_profile: dict[str, Any] = hints.get("global_profile") or {}
        # Composers see the domain answers and the agent answers as one flat
        # dict, agent winning on conflicts — the same precedence the real prompt
        # uses (general → specific).
        agent_profile: dict[str, Any] = {
            **(hints.get("domain_profile") or {}),
            **(hints.get("agent_profile") or {}),
        }
        memories: list[str] = [str(m) for m in (hints.get("memories") or [])]
        attachment: dict[str, Any] | None = hints.get("attachment")

        length_key = str(global_profile.get("preferred_response_length") or "balanced")
        plan = _LENGTH_PLAN.get(length_key, _LENGTH_PLAN["balanced"])

        composer = getattr(self, f"_compose_{agent_type}", self._compose_research)
        body = composer(request, global_profile, agent_profile, memories, plan)

        if attachment and attachment.get("name"):
            body += (
                f"\n\n**On your attachment `{attachment['name']}`** — "
                f"{attachment.get('chars', 0)} characters were read into context and used above."
            )

        applied = self._applied_personalization(global_profile, agent_profile, memories)
        if applied:
            body += "\n\n---\n**Personalization applied**\n" + _bullet_block(applied)

        content = body.strip()
        digest = hashlib.sha256(f"{agent_type}:{request}".encode()).hexdigest()[:12]
        return LLMResponse(
            content=content,
            model=self.default_model,
            provider=self.name,
            input_tokens=self._estimate_tokens(system, messages),
            output_tokens=max(1, len(content) // 4),
            stop_reason="end_turn",
            raw={"mode": "local-dev", "fingerprint": digest, "length_plan": length_key},
        )

    def _compose_media_spec(
        self, output_kind: str, request: str, hints: dict[str, Any]
    ) -> LLMResponse:
        """Deterministic JSON spec so visual agents work without a real model."""
        import json as _json

        topic = _topic(request)
        profile = hints.get("agent_profile") or {}
        domain_profile = hints.get("domain_profile") or {}

        if output_kind == "chart":
            labels, values = _extract_pairs(request)
            payload: dict[str, Any] = (
                {
                    "chart_type": str(profile.get("default_chart", "bar")).lower().replace(
                        "horizontal bar", "barh"
                    ),
                    "title": _sentence_case(topic)[:60] or "Chart",
                    "x_label": "",
                    "y_label": "",
                    "labels": labels,
                    "series": [{"name": "Series 1", "values": values}],
                    "note": "Rendered from the values in your message.",
                }
                if labels
                else {"error": "no label/value pairs were found in the message"}
            )
        else:
            payload = {
                "headline": _sentence_case(topic)[:70] or "Untitled",
                "subline": (
                    f"For {_join(domain_profile.get('audience'), 'your audience', 2)}."
                    if domain_profile.get("audience")
                    else ""
                ),
                "badge": str(domain_profile.get("brand_name") or ""),
                "cta": "Learn more",
                "palette": "brand",
                "layout": "left",
                "alt_text": f"Graphic with the headline {topic}",
            }

        content = _json.dumps(payload)
        return LLMResponse(
            content=content,
            model=self.default_model,
            provider=self.name,
            input_tokens=max(1, len(request) // 4),
            output_tokens=max(1, len(content) // 4),
            stop_reason="end_turn",
            raw={"mode": "local-dev", "output_kind": output_kind},
        )

    def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "model": self.default_model,
            "ok": True,
            "note": (
                "Local development provider. Set LLM_PROVIDER=bedrock with AWS "
                "credentials to use a real model."
            ),
        }

    # -------------------------------------------------------------- helpers
    @staticmethod
    def _last_user_message(messages: list[ChatMessage]) -> str:
        for message in reversed(messages):
            if message.role == "user":
                return message.content
        return messages[-1].content if messages else ""

    @staticmethod
    def _estimate_tokens(system: str | None, messages: list[ChatMessage]) -> int:
        total = len(system or "")
        total += sum(len(message.content) for message in messages)
        return max(1, total // 4)

    @staticmethod
    def _applied_personalization(
        global_profile: dict[str, Any],
        agent_profile: dict[str, Any],
        memories: list[str],
    ) -> list[str]:
        applied: list[str] = []
        if global_profile.get("preferred_response_length"):
            applied.append(
                f"Response length: **{global_profile['preferred_response_length']}** "
                f"(global profile)"
            )
        if global_profile.get("communication_style"):
            applied.append(
                f"Communication style: **{global_profile['communication_style']}** (global profile)"
            )
        interesting_keys = [
            key
            for key, value in agent_profile.items()
            if value
            and not key.endswith("history")
            and key not in {"created_at", "updated_at"}
        ][:4]
        if interesting_keys:
            rendered = ", ".join(
                f"{key.replace('_', ' ')}: {_join(agent_profile[key], '', 3)}"
                for key in interesting_keys
                if _join(agent_profile[key], "", 3)
            )
            if rendered:
                applied.append(f"Agent profile → {rendered}")
        if memories:
            applied.append(f"Learned preferences used: {len(memories)} → \"{memories[0]}\"")
        return applied

    # ------------------------------------------------------------ composers
    def _compose_technical(
        self,
        request: str,
        global_profile: dict[str, Any],
        profile: dict[str, Any],
        memories: list[str],
        plan: dict[str, Any],
    ) -> str:
        topic = _topic(request)
        level = str(profile.get("difficulty_level") or "Intermediate")
        languages = _as_list(profile.get("programming_languages")) or ["Python"]
        language = languages[0]
        prefs = _as_list(profile.get("coding_preferences"))
        wants_code = not prefs or any("code" in p.lower() for p in prefs)
        lang_tag = {
            "python": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "sql": "sql",
            "java": "java",
            "go": "go",
            "rust": "rust",
            "c++": "cpp",
            "c#": "csharp",
        }.get(language.lower(), "text")

        parts = [
             f"## {_sentence_case(topic)}",
            "",
            f"Calibrated for a **{level}** {language} developer"
            + (f" working with {_join(profile.get('frameworks'), '', 3)}"
               if _as_list(profile.get("frameworks")) else "")
            + ".",
            "",
            "**The idea**",
            "",
            _bullet_block(
                [
                    f"`{topic}` is the mechanism you reach for when you need to change or "
                    f"extend behaviour without editing the thing you are extending.",
                    "Three questions decide the design: what is the input, what is the "
                    "invariant you must not break, and where does failure surface?",
                    f"In {language}, the idiomatic form keeps the wrapper thin and pushes "
                    f"policy to the edges.",
                ][: plan["bullets"]]
            ),
        ]

        if wants_code:
            parts += [
                "",
                "**Worked example**",
                "",
                f"```{lang_tag}",
                self._code_sample(lang_tag, topic),
                "```",
            ]

        parts += [
            "",
            "**Where this bites in practice**",
            "",
            _bullet_block(
                [
                    "Losing metadata on the wrapped object (name, docstring, signature).",
                    "Swallowing exceptions so the real failure never reaches your logs.",
                    "Doing I/O inside a hot path and paying for it on every call.",
                    "Assuming single-threaded execution when the caller is concurrent.",
                ][: plan["bullets"]]
            ),
        ]
        if any("performance" in p.lower() for p in prefs):
            parts += [
                "",
                "**Performance note** — measure before you optimize: wrap the call site "
                "with `perf_counter`, look at p95 rather than the mean, and only then "
                "decide whether caching is worth the invalidation cost.",
            ]
        if any("test" in p.lower() for p in prefs):
            parts += [
                "",
                "**Test to add** — one test for the happy path, one that asserts the "
                "wrapped function's identity/metadata survives, one for the failure mode.",
            ]
        parts += [
            "",
            f"Target depth for this answer: {plan['words']} "
            f"({global_profile.get('preferred_response_length', 'balanced')}).",
        ]
        return "\n".join(parts)

    @staticmethod
    def _code_sample(lang_tag: str, topic: str) -> str:
        if lang_tag == "python":
            return (
                "import functools\nimport time\n\n\n"
                "def timed(func):\n"
                "    @functools.wraps(func)          # keeps __name__ / __doc__ intact\n"
                "    def wrapper(*args, **kwargs):\n"
                "        start = time.perf_counter()\n"
                "        try:\n"
                "            return func(*args, **kwargs)\n"
                "        finally:\n"
                "            elapsed = (time.perf_counter() - start) * 1000\n"
                "            print(f\"{func.__name__} took {elapsed:.2f} ms\")\n"
                "    return wrapper\n\n\n"
                "@timed\n"
                "def build_report(rows):\n"
                "    return sum(row[\"amount\"] for row in rows)\n"
            )
        if lang_tag in {"javascript", "typescript"}:
            return (
                "export function withTiming(fn) {\n"
                "  return async (...args) => {\n"
                "    const start = performance.now();\n"
                "    try {\n"
                "      return await fn(...args);\n"
                "    } finally {\n"
                "      console.log(`${fn.name} took ${(performance.now() - start).toFixed(1)}ms`);\n"
                "    }\n"
                "  };\n"
                "}\n"
            )
        if lang_tag == "sql":
            return (
                "SELECT\n"
                "    customer_id,\n"
                "    SUM(amount) AS revenue,\n"
                "    RANK() OVER (ORDER BY SUM(amount) DESC) AS revenue_rank\n"
                "FROM orders\n"
                "WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'\n"
                "GROUP BY customer_id\n"
                "ORDER BY revenue DESC\n"
                "LIMIT 20;\n"
            )
        return f"// {topic}\n// implementation sketch"

    def _compose_marketing(
        self,
        request: str,
        global_profile: dict[str, Any],
        profile: dict[str, Any],
        memories: list[str],
        plan: dict[str, Any],
    ) -> str:
        topic = _topic(request)
        platforms = _as_list(profile.get("platforms")) or ["LinkedIn"]
        platform = platforms[0]
        tone = str(profile.get("tone") or "Professional")
        style = str(profile.get("content_style") or profile.get("length") or "Short")
        audience = _join(profile.get("audience"), "your audience", 3)
        brand = str(profile.get("brand_name") or profile.get("brand") or "your brand")
        avoid = _as_list(profile.get("avoid"))
        concise_memory = any(
            "concise" in m.lower() or "short" in m.lower() or "brief" in m.lower()
            for m in memories
        )
        # Hashtags come from the subject, not from the instruction wording.
        keywords = _keywords(topic, 4)

        hook = f"{_sentence_case(topic)} is not a tooling upgrade. It is a staffing decision."
        if style.lower() == "storytelling":
            hook = (
                f"Last quarter a two-person team shipped what used to take six. "
                f"The difference was {topic}."
            )
        elif style.lower() == "educational":
            hook = f"Three things most teams get wrong about {topic}:"

        body_lines = [
            f"Most teams adopt {topic} to move faster. The ones who get value from it "
            f"start somewhere narrower: one repetitive workflow, one owner, one metric.",
            "Pick the task your team does weekly and resents. Automate that, measure the "
            "hours returned, then expand.",
        ]
        if style.lower() in {"short"} or concise_memory:
            body_lines = body_lines[:1]

        cta = {
            "Lead generation": "Curious what this looks like on your stack? DM me.",
            "Brand awareness": "What would you automate first?",
            "Community growth": "Drop your best automation win below.",
            "Thought leadership": "I'd push back on the hype — what's your read?",
            "Recruiting": "We're hiring engineers who think this way.",
            "Product launches": f"We just shipped this in {brand}. Link in comments.",
        }.get(
            str(profile.get("goals") or profile.get("goal") or ""),
            "What would you automate first?",
        )

        hashtags = " ".join(
            "#" + word.replace("-", "").replace(".", "").capitalize() for word in keywords[:3]
        )

        avoid_hashtags = any("hashtag" in item.lower() for item in avoid) or str(
            profile.get("use_hashtags") or ""
        ).lower().startswith("no")

        post = [hook, ""]
        post += [line for line in body_lines]
        post += ["", cta]
        if (
            platform.lower() in {"linkedin", "instagram", "x"}
            and hashtags
            and not avoid_hashtags
        ):
            post += ["", hashtags]

        parts = [
            f"**{platform} post — {tone.lower()} tone, {style.lower()} style, "
            f"for {audience}**",
            "",
            "\n".join(post).strip(),
            "",
            "---",
            "",
            "**Why this shape**",
            "",
            _bullet_block(
                [
                    f"Opens with a claim rather than a definition — {platform} rewards a "
                    f"first line that can stand alone in the feed.",
                    f"Kept to {style.lower()} length for {audience}.",
                    f"Voice matches your **{tone}** brand tone for {brand}.",
                    (
                        "Trimmed further because your saved preference asks for more "
                        "concise posts."
                        if concise_memory
                        else "Single call to action so the engagement signal is unambiguous."
                    ),
                ][: plan["bullets"]]
            ),
        ]
        if avoid:
            parts += [
                "",
                f"**Kept out** — {_join(avoid, '', 5)}, per your brand profile.",
            ]
        others = platforms[1:]
        if others:
            adaptations = []
            for other in others[:3]:
                lowered = other.lower()
                if lowered == "x":
                    adaptations.append("X: compress the hook to one sentence under 280 characters")
                elif lowered == "instagram":
                    adaptations.append("Instagram: lead with the caption, hashtags in a block below")
                elif lowered == "email":
                    adaptations.append("Email: turn the hook into the subject line")
                elif lowered == "blog":
                    adaptations.append("Blog: expand each line into its own H2 section")
                else:
                    adaptations.append(f"{other}: lead with the outcome instead of the claim")
            parts += [
                "",
                f"**Adapting for {_join(others, '', 3)}**",
                "",
                _bullet_block(adaptations),
            ]
        return "\n".join(parts)

    def _compose_education(
        self,
        request: str,
        global_profile: dict[str, Any],
        profile: dict[str, Any],
        memories: list[str],
        plan: dict[str, Any],
    ) -> str:
        topic = _topic(request)
        class_level = str(profile.get("class_level") or "Class 10")
        board = str(profile.get("board") or "CBSE")
        styles = _as_list(profile.get("learning_style"))
        subject = _first(profile.get("subjects"), "Science")

        parts = [
            f"## {_sentence_case(topic)}",
            "",
            f"*{board} · {class_level} · {subject}*",
            "",
            "**In one line**",
            "",
            f"{_sentence_case(topic)} is the process your syllabus describes as a change of "
            f"state driven by an input — and the exam expects you to name the input, the "
            f"change, and the output.",
            "",
            "**Step by step**",
            "",
            "\n".join(
                f"{index}. {step}"
                for index, step in enumerate(
                    [
                        "Write down what you are given and what is being asked.",
                        "Name the law/definition that connects them.",
                        "Substitute carefully, keeping units at every line.",
                        "State the result, then sanity-check the magnitude.",
                    ][: plan["bullets"]],
                    start=1,
                )
            ),
        ]
        if any("example" in style.lower() for style in styles) or not styles:
            parts += [
                "",
                "**Everyday example**",
                "",
                f"You already use {topic} without naming it — the same transformation "
                f"happens whenever the input is available and the conditions are right.",
            ]
        if any("visual" in style.lower() for style in styles):
            parts += [
                "",
                "**Diagram to draw** — label the input on the left, the transformation in "
                "the middle box, and both outputs on the right. Board examiners give marks "
                "for the labels, not the artwork.",
            ]
        if any("practice" in style.lower() for style in styles):
            parts += [
                "",
                "**Practice**",
                "",
                _bullet_block(
                    [
                        f"Define {topic} in one sentence (1 mark).",
                        f"State two conditions required for {topic} (2 marks).",
                        "Explain what happens when one condition is removed (3 marks).",
                    ]
                ),
                "",
                "*Answers:* the definition from above; the two inputs named in step 2; "
                "the process stalls and the output drops.",
            ]
        parts += [
            "",
            f"**Exam tip** — in {board} papers this carries the marks in the *explanation*, "
            f"so write the reason even when the question only says \"state\".",
        ]
        return "\n".join(parts)

    def _compose_career(
        self,
        request: str,
        global_profile: dict[str, Any],
        profile: dict[str, Any],
        memories: list[str],
        plan: dict[str, Any],
    ) -> str:
        topic = _topic(request)
        target = _first(profile.get("target_roles"), "Software Engineer")
        experience = str(profile.get("experience_years") or "0-1")
        skills = _as_list(profile.get("skills"))
        focus = _as_list(profile.get("interview_focus"))
        resume = str(profile.get("resume_summary") or "").strip()

        parts = [
            f"## {_sentence_case(topic)}",
            "",
            f"Target role: **{target}** · Experience band: **{experience}**",
            "",
            "**What a reviewer sees first**",
            "",
            _bullet_block(
                [
                    "Impact per bullet. A bullet without a number reads as a job description.",
                    f"Keyword overlap with the {target} posting — ATS filters on exact terms.",
                    "Recency: your most relevant work must be in the top third of page one.",
                    "Consistency between the resume, the LinkedIn headline, and the portfolio.",
                ][: plan["bullets"]]
            ),
            "",
            "**Rewrite pattern**",
            "",
            "Before: *Worked on backend APIs.*",
            f"After: *Built {_join(skills, 'Python/SQL', 2)} services handling 40k "
            f"requests/day; cut p95 latency 380ms → 120ms.*",
            "",
            "The shape is: action verb → what you built → the measured effect.",
        ]
        if resume:
            parts += [
                "",
                "**On your summary**",
                "",
                f"Your stored summary starts with \"{resume[:90]}\" — lead with the "
                f"{target} framing instead, and move the tooling list to a skills line "
                f"so the first sentence carries positioning, not inventory.",
            ]
        if skills:
            parts += [
                "",
                f"**Gap check for {target}** — you list {_join(skills, '', 5)}. For this "
                f"role the two things reviewers will look for and not find are system "
                f"design vocabulary and one production-scale story with numbers.",
            ]
        if focus:
            parts += [
                "",
                f"**Interview focus ({_join(focus, '', 3)})**",
                "",
                _bullet_block(
                    [
                        "Use STAR, but spend 60% of the answer on Action and Result.",
                        "Have three stories that can be recombined: conflict, failure, ownership.",
                        "Close every answer with the measurable outcome.",
                    ]
                ),
            ]
        return "\n".join(parts)

    def _compose_analytics(
        self,
        request: str,
        global_profile: dict[str, Any],
        profile: dict[str, Any],
        memories: list[str],
        plan: dict[str, Any],
    ) -> str:
        topic = _topic(request)
        tools = _as_list(profile.get("tools")) or ["Python / pandas"]
        tool = tools[0]
        charts = _join(profile.get("preferred_visualizations"), "bar and line charts", 3)
        experience = str(profile.get("experience") or "Intermediate")
        output_pref = str(profile.get("output_preference") or "Code + explanation")

        parts = [
            f"## {_sentence_case(topic)}",
            "",
            f"*{experience} analyst · primary tool: {tool} · preferred output: {output_pref}*",
            "",
            "**Analysis plan**",
            "",
            "\n".join(
                f"{index}. {step}"
                for index, step in enumerate(
                    [
                        "Profile the data: shape, dtypes, date range, one row per what?",
                        "Quantify missingness per column and decide drop vs impute per column.",
                        "Univariate pass: distribution and outliers for every numeric field.",
                        "Relationships: correlation for numerics, group means for categoricals.",
                        "Segment the headline metric by time and by the top dimension.",
                        "Write the three findings a decision-maker can act on.",
                    ][: plan["bullets"] + 1]
                    , start=1,
                )
            ),
        ]
        if output_pref != "Insights only":
            if "sql" in tool.lower():
                parts += [
                    "",
                    "```sql",
                    "SELECT date_trunc('month', order_date) AS month,\n"
                    "       region,\n"
                    "       SUM(amount)              AS revenue,\n"
                    "       COUNT(DISTINCT order_id) AS orders,\n"
                    "       SUM(amount) / NULLIF(COUNT(DISTINCT order_id), 0) AS aov\n"
                    "FROM sales\n"
                    "GROUP BY 1, 2\n"
                    "ORDER BY 1, revenue DESC;",
                    "```",
                ]
            else:
                parts += [
                    "",
                    "```python",
                    "import pandas as pd\n\n"
                    "df = pd.read_csv(\"sales.csv\", parse_dates=[\"order_date\"])\n\n"
                    "print(df.shape, df.dtypes, sep=\"\\n\")\n"
                    "print(df.isna().mean().sort_values(ascending=False).head(10))\n\n"
                    "monthly = (\n"
                    "    df.set_index(\"order_date\")\n"
                    "      .groupby([pd.Grouper(freq=\"MS\"), \"region\"])\n"
                    "      .agg(revenue=(\"amount\", \"sum\"), orders=(\"order_id\", \"nunique\"))\n"
                    "      .reset_index()\n"
                    ")\n"
                    "monthly[\"aov\"] = monthly.revenue / monthly.orders\n",
                    "```",
                ]
        parts += [
            "",
            f"**Visualization** — for this question use {charts}: time on the x-axis, the "
            f"metric on y, one line per segment. Keep the y-axis starting at zero for "
            f"revenue so the trend is not exaggerated.",
            "",
            "**What I can't conclude yet**",
            "",
            _bullet_block(
                [
                    "Causality — a segment lift could be mix shift rather than performance.",
                    "Seasonality needs at least two comparable periods.",
                    "Anything about customers who never enter this table.",
                ]
            ),
        ]
        return "\n".join(parts)

    def _compose_research(
        self,
        request: str,
        global_profile: dict[str, Any],
        profile: dict[str, Any],
        memories: list[str],
        plan: dict[str, Any],
    ) -> str:
        topic = _topic(request)
        depth = str(profile.get("preferred_depth") or "Balanced")
        sources = _as_list(profile.get("source_preferences")) or ["Official documentation"]
        fmt = str(profile.get("output_format") or "Structured report")

        parts = [
            f"## {_sentence_case(topic)}",
            "",
            f"*Depth: {depth} · Format: {fmt} · Source bias: {_join(sources, '', 3)}*",
            "",
            "**What it is**",
            "",
            f"{_sentence_case(topic)} names a pattern rather than a single technique: a "
            f"retrieval step that narrows the input, and a generation step that is "
            f"constrained by what was retrieved.",
            "",
            "**Why it matters**",
            "",
            _bullet_block(
                [
                    "It decouples knowledge from weights, so updating facts is a data "
                    "operation rather than a training run.",
                    "It gives you an audit trail: every claim can be traced to a chunk.",
                    "It shifts the hard problem from generation quality to retrieval quality.",
                ][: plan["bullets"]]
            ),
            "",
            "**How it works**",
            "",
            "\n".join(
                f"{index}. {step}"
                for index, step in enumerate(
                    [
                        "Chunk and embed the corpus; store vectors with metadata.",
                        "Embed the query, retrieve top-k by cosine similarity, optionally rerank.",
                        "Build a prompt that carries the retrieved context plus the question.",
                        "Generate with an instruction to answer only from context.",
                    ][: plan["bullets"]],
                    start=1,
                )
            ),
            "",
            "**Trade-offs**",
            "",
            _bullet_block(
                [
                    "Chunk size: large chunks preserve context but dilute the embedding.",
                    "Latency: reranking improves precision and costs a round trip.",
                    "Failure mode shifts from hallucination to confident retrieval of the "
                    "wrong passage.",
                ]
            ),
            "",
            "**Where to read next**",
            "",
            _bullet_block(
                [
                    f"{sources[0]} for the canonical description of the pattern.",
                    "The original retrieval-augmented generation paper (Lewis et al., 2020) "
                    "for the framing.",
                    "Your vector database's own docs for index and distance-metric choices.",
                ]
            ),
            "",
            "**Confidence** — high on the mechanism, medium on which retrieval strategy "
            "wins for a given corpus; that is empirical. I have not verified any figure "
            "beyond the paper reference above, so treat benchmark numbers as unchecked.",
        ]
        return "\n".join(parts)

    def _compose_creative(
        self,
        request: str,
        global_profile: dict[str, Any],
        profile: dict[str, Any],
        memories: list[str],
        plan: dict[str, Any],
    ) -> str:
        topic = _topic(request)
        genre = _first(profile.get("preferred_genres"), "Sci-fi")
        style = str(profile.get("writing_style") or "Descriptive")
        tone = str(profile.get("tone") or "Serious")
        length = str(profile.get("length_preference") or "Short (150-500)")

        title = _sentence_case(topic)[:60] or "The Quiet Hour"
        story = [
            f"### {title}",
            "",
            "The relay tower had been silent for eleven days when Maya finally climbed it.",
            "",
            "Frost held the ladder rungs the way rust holds a promise — not firmly, but "
            "long enough. At the top she found the transmitter still warm, still cycling, "
            "still sending the same fourteen seconds of audio into a sky that had stopped "
            "answering.",
            "",
            "She listened to it twice. The first time she heard her mother's voice. The "
            "second time she heard the gap underneath it, the half-breath where someone "
            "else had been standing close enough to be recorded and careful enough not to "
            "speak.",
            "",
            "Maya cut the loop. In the silence that followed, the tower made a sound she "
            "had never heard it make: nothing at all. And somewhere below, in a town that "
            "had agreed for eleven days that the broadcast was a comfort, four hundred "
            "people looked up at once.",
        ]
        if "micro" in length.lower():
            story = story[:6]

        parts = [
            "\n".join(story),
            "",
            "---",
            "",
            f"*{genre} · {style.lower()} · {tone.lower()} · {length}*",
            "",
            "**Craft notes**",
            "",
            _bullet_block(
                [
                    "The turn is the gap in the recording, not the climb — the reveal is "
                    "structural, so it survives a re-read.",
                    f"Kept the register {tone.lower()} and the prose {style.lower()}: "
                    f"concrete nouns, no abstraction until the last line.",
                    "The ending widens from one character to a town, which is where the "
                    "story's stakes actually live.",
                ][: plan["bullets"]]
            ),
            "",
            "**If you want a different direction** — make the recording Maya's own voice "
            "(identity), or let the town choose to restart the loop (complicity).",
        ]
        return "\n".join(parts)
