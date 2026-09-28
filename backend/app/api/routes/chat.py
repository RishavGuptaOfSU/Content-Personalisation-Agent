"""Chat routes: the LangGraph pipeline, streaming, uploads and media serving."""

from __future__ import annotations

import json
import time
from collections.abc import Iterator

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.agents.catalog import get_agent_spec
from app.agents.graph import (
    CHAT_GRAPH_NODES,
    finalize_chat_turn,
    prepare_chat_turn,
    run_chat_pipeline,
)
from app.agents.runtime import AgentResult, get_agent, supports_streaming
from app.agents.scope import handoff_message
from app.api.deps import CurrentUser, DbSession, resolve_agent_key
from app.core.logging import get_logger
from app.llm.base import LLMProviderError, LLMResponse
from app.llm.registry import get_llm_provider, provider_status
from app.media import media_status
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MemoryUsed,
    MessageRead,
    PersonalizationTrace,
    RoutingInfo,
    ScopeInfo,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

_MAX_UPLOAD_BYTES = 1_000_000
_ALLOWED_UPLOAD_SUFFIXES = (
    ".txt", ".md", ".csv", ".json", ".tsv", ".log", ".py", ".sql", ".yaml", ".yml",
)


# ------------------------------------------------------------------- helpers
def _routing_info(state) -> RoutingInfo:  # type: ignore[no-untyped-def]
    routing = state["routing"]
    spec = get_agent_spec(routing.agent_key)
    return RoutingInfo(
        agent_key=routing.agent_key,
        domain=spec.domain,
        agent_name=spec.name,
        source=routing.source,
        confidence=routing.confidence,
        reason=routing.reason,
        candidates=routing.scores,
    )


def _scope_info(state) -> ScopeInfo:  # type: ignore[no-untyped-def]
    verdict = state["scope"]
    return ScopeInfo(
        in_scope=verdict.in_scope,
        reason=verdict.reason,
        suggested_agent_key=verdict.suggested_key,
        suggested_agent_name=verdict.suggested_name,
    )


def _system_prompt_preview(state, limit: int = 700) -> str:  # type: ignore[no-untyped-def]
    """The prompt the agent actually sends, including its scope contract.

    ``context.system_prompt`` is only the output contract; the scope section and
    task instructions are assembled by the agent, so ask the agent for the real
    thing rather than showing a partial prompt in the UI.
    """
    try:
        prompt, _hints = get_agent(state["agent_key"]).build_prompt(state["context"])
    except Exception:  # pragma: no cover - never break a response over a preview
        prompt = state["context"].system_prompt
    return prompt[:limit]


def _trace(state, provider_name: str, model: str) -> PersonalizationTrace:  # type: ignore[no-untyped-def]
    context = state["context"]
    spec = get_agent_spec(state["agent_key"])
    return PersonalizationTrace(
        agent_key=spec.key,
        domain=spec.domain,
        output_kind=spec.output_kind.value,
        global_profile_summary=context.global_summary,
        domain_profile_summary=context.domain_summary,
        agent_profile_summary=context.agent_summary,
        memories_used=[
            MemoryUsed(
                id=scored.memory.id,
                content=scored.memory.content,
                kind=scored.memory.kind,
                scope=scored.memory.agent_key or scored.memory.domain or "global",
                similarity=round(scored.similarity, 4),
                importance=round(scored.memory.importance, 3),
                pinned=scored.pinned,
                occurrences=scored.memory.occurrences,
            )
            for scored in context.memories
        ],
        short_term_messages=len(context.short_term),
        context_characters=context.context_characters,
        system_prompt_preview=_system_prompt_preview(state),
        provider=provider_name,
        model=model,
    )


def _build_response(state) -> ChatResponse:  # type: ignore[no-untyped-def]
    response = state["result"].llm_response
    return ChatResponse(
        conversation_id=state["conversation"].id,
        conversation_title=state["conversation"].title,
        user_message=MessageRead.model_validate(state["user_message"]),
        assistant_message=MessageRead.model_validate(state["assistant_message"]),
        routing=_routing_info(state),
        scope=_scope_info(state),
        personalization=_trace(state, response.provider, response.model),
        new_memories=state.get("new_memories") or [],
        latency_ms=state.get("latency_ms") or 0,
    )


# ---------------------------------------------------------------------- chat
@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, user: CurrentUser, db: DbSession) -> ChatResponse:
    """Full pipeline: auth → router → scope → profiles → memory → agent → persist.

    Visual agents (post images, ad creatives, posters, charts) return their
    rendered file in ``assistant_message.media``.
    """
    agent_key = resolve_agent_key(payload.agent_key)
    try:
        state = run_chat_pipeline(
            db,
            user_id=user.id,
            request=payload.message,
            explicit_agent=agent_key,
            conversation_id=payload.conversation_id,
            attachment_name=payload.attachment_name,
            attachment_text=payload.attachment_text,
        )
    except LLMProviderError as exc:
        db.rollback()
        logger.error("LLM provider error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The language model provider is unavailable. Check LLM_PROVIDER and "
                "the provider credentials on the server."
            ),
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return _build_response(state)


def _sse(event: str, payload: object) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, default=str)}\n\n"


class _FenceFilter:
    """Hide fenced code blocks from the stream when the reply must be prose-only."""

    def __init__(self, active: bool) -> None:
        self.active = active
        self.in_fence = False
        self.pending = ""

    def feed(self, chunk: str) -> str:
        if not self.active:
            return chunk
        self.pending += chunk
        out = ""
        while "```" in self.pending:
            before, _, rest = self.pending.partition("```")
            if not self.in_fence:
                out += before
            self.pending = rest
            self.in_fence = not self.in_fence
        hold = 2 if self.pending.endswith("``") else 1 if self.pending.endswith("`") else 0
        emit = self.pending[: len(self.pending) - hold] if hold else self.pending
        self.pending = self.pending[len(emit) :]
        return out + (emit if not self.in_fence else "")

    def flush(self) -> str:
        if not self.active or self.in_fence:
            return ""
        remainder, self.pending = self.pending, ""
        return remainder


@router.post("/stream")
def chat_stream(payload: ChatRequest, user: CurrentUser, db: DbSession) -> StreamingResponse:
    """Streaming variant for text agents.

    Emits ``meta`` (routing + scope + personalization) before generation starts,
    then ``delta`` chunks, then ``done`` with the persisted turn.

    Visual agents cannot stream — an image has to be rendered before it exists —
    so they are generated in one step and delivered in the ``done`` event.
    """
    agent_key = resolve_agent_key(payload.agent_key)

    def event_stream() -> Iterator[str]:
        started = time.perf_counter()
        try:
            state = prepare_chat_turn(
                db,
                user_id=user.id,
                request=payload.message,
                explicit_agent=agent_key,
                conversation_id=payload.conversation_id,
                attachment_name=payload.attachment_name,
                attachment_text=payload.attachment_text,
            )
        except ValueError as exc:
            yield _sse("error", {"detail": str(exc)})
            return
        except Exception as exc:  # pragma: no cover - defensive
            db.rollback()
            logger.exception("Streaming preparation failed")
            yield _sse("error", {"detail": f"Could not prepare the request: {exc}"})
            return

        spec = get_agent_spec(state["agent_key"])
        provider = get_llm_provider()
        verdict = state["scope"]
        streaming = supports_streaming(spec.key) and verdict.in_scope

        yield _sse(
            "meta",
            {
                "routing": _routing_info(state).model_dump(),
                "scope": _scope_info(state).model_dump(),
                "personalization": _trace(state, provider.name, provider.default_model).model_dump(),
                "streaming": streaming,
                "output_kind": spec.output_kind.value,
            },
        )

        # Out of scope: hand off without spending a model call.
        if not verdict.in_scope:
            content = handoff_message(spec, verdict)
            for word in content.split(" "):
                yield _sse("delta", {"text": word + " "})
            result = AgentResult(
                content=content,
                output_kind="text",
                llm_response=LLMResponse(
                    content=content, model="scope-guard", provider="scope-guard"
                ),
                incomplete_reason="out_of_scope",
            )
        elif not streaming:
            # Image/chart agents: render, then deliver in one go.
            yield _sse("status", {"message": f"Generating the {spec.output_kind.value}…"})
            try:
                result = get_agent(spec.key).run(state["context"])
            except LLMProviderError as exc:
                db.rollback()
                yield _sse("error", {"detail": str(exc)})
                return
            if result.content:
                yield _sse("delta", {"text": result.content})
        else:
            agent = get_agent(spec.key)
            constraints = agent.constraints(state["context"])
            fence_filter = _FenceFilter(
                constraints["brevity"] or constraints["no_code"] or constraints["trivial"]
            )
            chunks: list[str] = []
            try:
                for piece in agent.stream(state["context"]):  # type: ignore[attr-defined]
                    if not piece:
                        continue
                    chunks.append(piece)
                    visible = fence_filter.feed(piece)
                    if visible:
                        yield _sse("delta", {"text": visible})
                tail = fence_filter.flush()
                if tail:
                    yield _sse("delta", {"text": tail})
            except LLMProviderError as exc:
                db.rollback()
                logger.error("Streaming generation failed: %s", exc)
                yield _sse("error", {"detail": str(exc)})
                return

            content = agent.post_process("".join(chunks), state["context"])
            if not content.strip():
                db.rollback()
                yield _sse("error", {"detail": "The model returned an empty response."})
                return
            result = AgentResult(
                content=content,
                output_kind="text",
                llm_response=LLMResponse(
                    content=content,
                    model=provider.default_model,
                    provider=provider.name,
                    output_tokens=max(1, len(content) // 4),
                    stop_reason="stream_end",
                    raw={"streamed": True},
                ),
            )

        try:
            state = finalize_chat_turn(state, result)
        except Exception as exc:  # pragma: no cover - defensive
            db.rollback()
            logger.exception("Could not persist the streamed turn")
            yield _sse("error", {"detail": f"Could not save the conversation: {exc}"})
            return

        state["latency_ms"] = int((time.perf_counter() - started) * 1000)
        yield _sse("done", _build_response(state).model_dump())

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# -------------------------------------------------------------------- uploads
@router.post("/upload")
async def upload_attachment(user: CurrentUser, file: UploadFile = File(...)) -> dict[str, object]:
    """Read a small text/CSV file so its content can travel with the next message.

    Useful for the Chart Builder (paste a CSV) and the analysis agents. The file
    itself is not stored: the extracted text is returned to the client.
    """
    filename = file.filename or "attachment"
    if not filename.lower().endswith(_ALLOWED_UPLOAD_SUFFIXES):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Supported file types: {', '.join(_ALLOWED_UPLOAD_SUFFIXES)}",
        )

    raw = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(raw) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is larger than 1 MB",
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("latin-1")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File is not readable as text",
            ) from exc

    truncated = text[:40000]
    return {
        "name": filename,
        "characters": len(truncated),
        "truncated": len(text) > len(truncated),
        "text": truncated,
    }


@router.get("/pipeline")
def pipeline_info(user: CurrentUser) -> dict[str, object]:
    """Introspection: graph nodes, providers and renderers."""
    return {
        "graph_nodes": list(CHAT_GRAPH_NODES),
        "providers": provider_status(),
        "media": media_status(),
    }
