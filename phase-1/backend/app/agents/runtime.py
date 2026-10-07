"""Agent runtime.

One class per *output kind*, driven entirely by the catalog:

    TextAgent   — prose, code, plans (30 agents)
    ImageAgent  — model returns a JSON design spec, renderer produces a PNG
    ChartAgent  — model returns a JSON chart spec, matplotlib produces a PNG

The agents themselves hold no domain knowledge: the prompt is assembled from the
:class:`AgentSpec` (scope, instructions, out-of-scope list) plus the user's
three-level profile, so adding an agent means adding catalog data, not code.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.agents.catalog import AgentSpec, OutputKind, get_agent_spec
from app.agents.scope import scope_prompt_section
from app.core.config import settings
from app.core.logging import get_logger
from app.core.request_hints import detect_request_constraints
from app.llm.base import LLMProviderError, LLMResponse
from app.llm.registry import get_llm_provider
from app.media import (
    ChartSeries,
    ChartSpec,
    ImageSpec,
    MediaGenerationError,
    RenderedMedia,
    get_chart_renderer,
    get_image_renderer,
)
from app.services.personalization import PersonalizedContext

logger = get_logger(__name__)


@dataclass(slots=True)
class AgentResult:
    """What an agent produced for one turn."""

    content: str
    output_kind: str
    llm_response: LLMResponse
    media: list[RenderedMedia] = field(default_factory=list)
    #: Set when the agent could not produce its deliverable (e.g. no data given).
    incomplete_reason: str | None = None

    @property
    def media_payload(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.media]


# --------------------------------------------------------------------- helpers
_FENCE_RE = re.compile(r"\n?```.*?```\n?", re.S)
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+.*$", re.M)


def _extract_json(raw: str) -> dict[str, Any] | None:
    """Pull the first JSON object out of a model reply.

    Small models wrap JSON in prose or fences despite instructions, so this is
    tolerant: strip fences, then take the outermost balanced braces.
    """
    if not raw:
        return None
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S).strip()

    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    payload = json.loads(text[start : index + 1])
                except json.JSONDecodeError:
                    return None
                return payload if isinstance(payload, dict) else None
    return None


def _as_float_list(values: Any) -> list[float]:
    numbers: list[float] = []
    for value in values or []:
        try:
            numbers.append(float(str(value).replace(",", "").replace("₹", "").strip()))
        except (TypeError, ValueError):
            continue
    return numbers


# ----------------------------------------------------------------- base class
class BaseAgent:
    """Shared prompt assembly and model invocation."""

    def __init__(self, spec: AgentSpec) -> None:
        self.spec = spec

    # -- identity ---------------------------------------------------------
    @property
    def key(self) -> str:
        return self.spec.key

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def domain(self) -> str:
        return self.spec.domain

    @property
    def output_kind(self) -> OutputKind:
        return self.spec.output_kind

    # -- prompt -----------------------------------------------------------
    def constraints(self, context: PersonalizedContext) -> dict[str, bool]:
        return detect_request_constraints(str(context.hints.get("request") or ""))

    def temperature(self) -> float:
        return settings.LLM_TEMPERATURE

    def max_tokens(self, context: PersonalizedContext | None = None) -> int:
        if context is not None:
            flags = self.constraints(context)
            if flags["trivial"]:
                return settings.TRIVIAL_REPLY_MAX_TOKENS
            if flags["brevity"]:
                return min(settings.LLM_MAX_TOKENS, 320)
        return settings.LLM_MAX_TOKENS

    def build_prompt(self, context: PersonalizedContext) -> tuple[str, dict[str, Any]]:
        """System prompt: scope contract, task instructions, output contract."""
        flags = self.constraints(context)
        hints: dict[str, Any] = dict(context.hints)
        hints["agent_key"] = self.key
        hints["output_kind"] = self.output_kind.value

        if flags["trivial"]:
            # A greeting needs neither the scope contract nor the task rules.
            return (
                f"You are the {self.name}. The user has greeted you or said thanks.\n"
                f"Reply in at most two short sentences: greet them back and say in one "
                f"clause what you do ({self.spec.tagline}).\n"
                "No headings, no lists, no code, no explanation of earlier topics.",
                hints,
            )

        parts = [
            scope_prompt_section(self.spec),
            "",
            "=== HOW YOU WORK ===",
            self.spec.instructions,
            "",
            context.system_prompt,
        ]
        extra = self.output_contract(context)
        if extra:
            parts += ["", extra]

        hard_rules = [
            "An explicit instruction in the user's latest message overrides the "
            "preferences above — but never overrides your scope.",
        ]
        if flags["brevity"]:
            hard_rules.append(
                "The user asked for a very short answer: obey the length they named, "
                "prose only, no code block or heading."
            )
        if flags["no_code"]:
            hard_rules.append("Do NOT include any code block.")
        if flags["bullets_only"]:
            hard_rules.append("Bullet points only, no paragraphs.")
        parts += ["", "=== PRIORITY (highest) ===", *[f"- {rule}" for rule in hard_rules]]

        return "\n".join(parts), hints

    def output_contract(self, context: PersonalizedContext) -> str:
        """Extra output rules for this output kind. Overridden by subclasses."""
        return ""

    # -- generation -------------------------------------------------------
    def _invoke(self, context: PersonalizedContext) -> LLMResponse:
        system_prompt, hints = self.build_prompt(context)
        return get_llm_provider().generate(
            context.to_messages(),
            system=system_prompt,
            temperature=self.temperature(),
            max_tokens=self.max_tokens(context),
            hints=hints,
        )

    def run(self, context: PersonalizedContext) -> AgentResult:
        raise NotImplementedError

    def post_process(self, content: str, context: PersonalizedContext) -> str:
        cleaned = (content or "").strip()
        flags = self.constraints(context)
        if flags["no_code"] or flags["brevity"] or flags["trivial"]:
            without_code = _FENCE_RE.sub("\n", cleaned).strip()
            if len(without_code) >= 40:
                cleaned = without_code
        if flags["brevity"] or flags["trivial"]:
            without_headings = _HEADING_RE.sub("", cleaned).strip()
            if len(without_headings) >= 40:
                cleaned = without_headings
        return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


# ----------------------------------------------------------------- text agents
class TextAgent(BaseAgent):
    """Produces prose, code, tables or plans."""

    def run(self, context: PersonalizedContext) -> AgentResult:
        response = self._invoke(context)
        content = self.post_process(response.content, context)
        if not content:
            raise LLMProviderError("The model returned an empty response.")
        return AgentResult(content=content, output_kind=OutputKind.TEXT.value, llm_response=response)

    def stream(self, context: PersonalizedContext):
        """Yield text chunks. Only text agents stream — media must be complete."""
        system_prompt, hints = self.build_prompt(context)
        yield from get_llm_provider().stream(
            context.to_messages(),
            system=system_prompt,
            temperature=self.temperature(),
            max_tokens=self.max_tokens(context),
            hints=hints,
        )


# ---------------------------------------------------------------- image agents
class ImageAgent(BaseAgent):
    """Model designs the graphic as JSON; the renderer produces the file."""

    def temperature(self) -> float:
        return 0.6  # some variation in copy is desirable

    def max_tokens(self, context: PersonalizedContext | None = None) -> int:
        return 420  # a JSON spec is short; no need for the full budget

    def output_contract(self, context: PersonalizedContext) -> str:
        return (
            "=== OUTPUT FORMAT (strict) ===\n"
            "Return ONLY the JSON object described above. No markdown, no code "
            "fence, no commentary before or after. The text you choose is rendered "
            "onto the image exactly as written, so keep every field short."
        )

    def _size(self, profile: dict[str, Any]) -> tuple[int, int]:
        sizes: dict[str, list[int]] = self.spec.options.get("sizes", {})
        default = self.spec.options.get("default_size", [1200, 627])
        for value in profile.values():
            if isinstance(value, str) and value in sizes:
                width, height = sizes[value]
                return int(width), int(height)
        return int(default[0]), int(default[1])

    def run(self, context: PersonalizedContext) -> AgentResult:
        response = self._invoke(context)
        payload = _extract_json(response.content)

        agent_profile: dict[str, Any] = context.hints.get("agent_profile") or {}
        domain_profile: dict[str, Any] = context.hints.get("domain_profile") or {}

        if payload is None or not str(payload.get("headline", "")).strip():
            # The model failed to produce a spec. Fall back to the request itself
            # as the headline rather than returning nothing renderable.
            request = str(context.hints.get("request") or "").strip()
            logger.warning("%s: no usable JSON spec; falling back to the request text", self.key)
            payload = {"headline": request[:90] or "Untitled", "subline": "", "alt_text": ""}

        width, height = self._size({**domain_profile, **agent_profile})
        brand_colors = [
            part.strip()
            for part in str(domain_profile.get("brand_colors") or "").replace(";", ",").split(",")
            if part.strip()
        ]

        spec = ImageSpec(
            headline=str(payload.get("headline", "")),
            subline=str(payload.get("subline", "") or ""),
            badge=str(payload.get("badge", "") or "") or str(domain_profile.get("brand_name", "") or ""),
            cta=str(payload.get("cta", "") or ""),
            palette=str(payload.get("palette", "brand") or "brand"),  # type: ignore[arg-type]
            layout=str(payload.get("layout", "centered") or "centered"),  # type: ignore[arg-type]
            alt_text=str(payload.get("alt_text", "") or ""),
            logo_text=str(agent_profile.get("include_logo_text", "") or ""),
            brand_colors=brand_colors,
            width=width,
            height=height,
            style=str(agent_profile.get("style") or agent_profile.get("mood") or ""),
        )

        try:
            media = get_image_renderer().render(spec, filename_hint=self.spec.slug)
        except MediaGenerationError as exc:
            logger.error("%s: rendering failed: %s", self.key, exc)
            return AgentResult(
                content=f"I could not render the image: {exc}",
                output_kind=OutputKind.IMAGE.value,
                llm_response=response,
                incomplete_reason=str(exc),
            )

        return AgentResult(
            content=self._caption(spec, media),
            output_kind=OutputKind.IMAGE.value,
            llm_response=response,
            media=[media],
        )

    def _caption(self, spec: ImageSpec, media: RenderedMedia) -> str:
        """The short text shown beside the image. The image is the deliverable."""
        lines = [f"**{spec.headline}**"]
        if spec.subline:
            lines.append(spec.subline)
        details = [f"{media.width}×{media.height}"]
        if spec.cta:
            details.append(f"CTA: {spec.cta}")
        if spec.palette:
            details.append(f"{spec.palette} palette")
        lines += ["", f"*{' · '.join(details)}*"]
        return "\n".join(lines)


# ---------------------------------------------------------------- chart agents
class ChartAgent(BaseAgent):
    """Model extracts the data into a chart spec; matplotlib renders it."""

    def temperature(self) -> float:
        return 0.1  # data extraction must be literal

    def max_tokens(self, context: PersonalizedContext | None = None) -> int:
        return 700

    def output_contract(self, context: PersonalizedContext) -> str:
        return (
            "=== OUTPUT FORMAT (strict) ===\n"
            "Return ONLY the JSON object described above — no markdown, no fence, "
            "no commentary. Every number must come from the user's message or "
            "attachment; never invent, round or extrapolate values."
        )

    def run(self, context: PersonalizedContext) -> AgentResult:
        response = self._invoke(context)
        payload = _extract_json(response.content)
        agent_profile: dict[str, Any] = context.hints.get("agent_profile") or {}

        if payload is None:
            return AgentResult(
                content=(
                    "I could not read a chart specification from that. Send the data as "
                    "label/value pairs, for example: `Jan 120, Feb 150, Mar 180`."
                ),
                output_kind=OutputKind.CHART.value,
                llm_response=response,
                incomplete_reason="no chart specification returned",
            )

        if payload.get("error"):
            return AgentResult(
                content=f"I need data before I can plot anything. {payload['error']}",
                output_kind=OutputKind.CHART.value,
                llm_response=response,
                incomplete_reason=str(payload["error"]),
            )

        series_payload = payload.get("series") or []
        series = [
            ChartSeries(
                name=str(item.get("name") or f"Series {index + 1}"),
                values=_as_float_list(item.get("values")),
            )
            for index, item in enumerate(series_payload)
            if isinstance(item, dict)
        ]

        spec = ChartSpec(
            chart_type=str(payload.get("chart_type") or "bar").lower(),  # type: ignore[arg-type]
            title=str(payload.get("title") or ""),
            x_label=str(payload.get("x_label") or ""),
            y_label=str(payload.get("y_label") or ""),
            labels=[str(label) for label in (payload.get("labels") or [])],
            series=series,
            note=str(payload.get("note") or ""),
            style=str(agent_profile.get("style") or "Clean light"),
            show_values=str(agent_profile.get("show_values", "Yes")).lower() != "no",
        )

        try:
            media = get_chart_renderer().render(spec, filename_hint=self.spec.slug)
        except MediaGenerationError as exc:
            logger.warning("%s: chart could not be rendered: %s", self.key, exc)
            return AgentResult(
                content=(
                    f"I could not plot that: {exc}\n\n"
                    "Send the data as label/value pairs and I will chart it."
                ),
                output_kind=OutputKind.CHART.value,
                llm_response=response,
                incomplete_reason=str(exc),
            )

        caption = [f"**{spec.title or 'Chart'}**"]
        if spec.note:
            caption.append(spec.note)
        caption += ["", f"*{spec.chart_type} chart · {media.width}×{media.height}*"]
        return AgentResult(
            content="\n".join(caption),
            output_kind=OutputKind.CHART.value,
            llm_response=response,
            media=[media],
        )


# -------------------------------------------------------------------- registry
_CLASS_FOR_KIND: dict[OutputKind, type[BaseAgent]] = {
    OutputKind.TEXT: TextAgent,
    OutputKind.IMAGE: ImageAgent,
    OutputKind.CHART: ChartAgent,
}

_instances: dict[str, BaseAgent] = {}


def get_agent(agent_key: str) -> BaseAgent:
    """The runtime instance for a catalog agent key."""
    spec = get_agent_spec(agent_key)
    if spec.key not in _instances:
        _instances[spec.key] = _CLASS_FOR_KIND[spec.output_kind](spec)
    return _instances[spec.key]


def supports_streaming(agent_key: str) -> bool:
    """Only text agents stream; media has to be rendered before it can be sent."""
    return get_agent_spec(agent_key).output_kind is OutputKind.TEXT
