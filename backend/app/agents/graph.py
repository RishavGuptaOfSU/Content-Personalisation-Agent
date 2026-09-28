"""LangGraph orchestration for one chat turn.

    load_user
        ↓
    router                 (explicit selection > keywords > LLM two-stage)
        ↓
    scope_guard            (hand off if this agent does not own the request)
        ↓
    load_global_profile
        ↓
    load_domain_profile
        ↓
    load_agent_profile
        ↓
    retrieve_memory
        ↓
    build_context          (personalization engine)
        ↓
    generate_response      (text, or JSON spec → rendered image/chart)
        ↓
    store_message          (persist turn + media, capture durable memories)
        ↓
    END

``process_feedback`` is a separate compiled graph (``feedback_graph.py``).
"""

from __future__ import annotations

import time
import uuid
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.agents.catalog import get_agent_spec
from app.agents.router import RoutingDecision, get_router
from app.agents.runtime import AgentResult, get_agent
from app.agents.scope import ScopeVerdict, assess, handoff_message
from app.core.logging import get_logger
from app.llm.base import LLMProviderError, LLMResponse
from app.memory.service import get_memory_service
from app.memory.vector_store import ScoredMemory
from app.models.conversation import Conversation, Message
from app.models.profiles import AgentProfile, DomainProfile, GlobalProfile
from app.models.user import User
from app.services.conversation_service import derive_title, get_conversation_service
from app.services.personalization import PersonalizedContext, get_personalization_engine
from app.services.profile_service import get_profile_service

logger = get_logger(__name__)


def _keep_last(_current: Any, incoming: Any) -> Any:
    return incoming


class ChatState(TypedDict):
    """Every key is explicitly nullable and initialised: LangGraph materialises a
    default for any declared-but-unwritten channel, so relying on "key absent"
    would hand nodes an empty ORM instance instead of ``None``."""

    db: Annotated[Session, _keep_last]
    user_id: Annotated[uuid.UUID, _keep_last]
    request: Annotated[str, _keep_last]
    explicit_agent: Annotated[str | None, _keep_last]
    conversation_id: Annotated[uuid.UUID | None, _keep_last]
    attachment_name: Annotated[str | None, _keep_last]
    attachment_text: Annotated[str | None, _keep_last]

    user: Annotated[User | None, _keep_last]
    global_profile: Annotated[GlobalProfile | None, _keep_last]
    domain_profile: Annotated[DomainProfile | None, _keep_last]
    agent_profile: Annotated[AgentProfile | None, _keep_last]
    conversation: Annotated[Conversation | None, _keep_last]
    routing: Annotated[RoutingDecision | None, _keep_last]
    agent_key: Annotated[str | None, _keep_last]
    scope: Annotated[ScopeVerdict | None, _keep_last]
    memories: Annotated[list[ScoredMemory] | None, _keep_last]
    context: Annotated[PersonalizedContext | None, _keep_last]
    result: Annotated[AgentResult | None, _keep_last]
    user_message: Annotated[Message | None, _keep_last]
    assistant_message: Annotated[Message | None, _keep_last]
    new_memories: Annotated[list[str] | None, _keep_last]
    started_at: Annotated[float | None, _keep_last]
    latency_ms: Annotated[int | None, _keep_last]


# ---------------------------------------------------------------------- nodes
def load_user(state: ChatState) -> dict[str, Any]:
    db: Session = state["db"]
    user = db.get(User, state["user_id"])
    if user is None or not user.is_active:
        raise ValueError("User not found or inactive")
    return {"user": user, "started_at": time.perf_counter()}


def router(state: ChatState) -> dict[str, Any]:
    db: Session = state["db"]
    conversation: Conversation | None = None
    conversation_agent: str | None = None

    if state.get("conversation_id"):
        conversation = get_conversation_service().get(
            db, user_id=state["user_id"], conversation_id=state["conversation_id"]
        )
        if conversation is None:
            raise ValueError("Conversation not found")
        conversation_agent = conversation.agent_key

    decision = get_router().route(
        state["request"],
        explicit_agent=state.get("explicit_agent"),
        conversation_agent=conversation_agent,
    )
    logger.info(
        "Router -> %s (%s, %.2f)", decision.agent_key, decision.source, decision.confidence
    )
    result: dict[str, Any] = {"routing": decision, "agent_key": decision.agent_key}
    if conversation is not None:
        result["conversation"] = conversation
    return result


def scope_guard(state: ChatState) -> dict[str, Any]:
    """Only meaningful when the user picked the agent — the router already
    chooses an owner, so a routed request is in scope by construction."""
    routing: RoutingDecision = state["routing"]
    if routing.source != "explicit":
        return {"scope": ScopeVerdict(True, 0.0, reason="Chosen by the router.")}
    return {"scope": assess(state["request"], state["agent_key"])}


def load_global_profile(state: ChatState) -> dict[str, Any]:
    return {
        "global_profile": get_profile_service().get_or_create_global_profile(
            state["db"], state["user"]
        )
    }


def load_domain_profile(state: ChatState) -> dict[str, Any]:
    spec = get_agent_spec(state["agent_key"])
    return {
        "domain_profile": get_profile_service().get_domain_profile(
            state["db"], state["user_id"], spec.domain
        )
    }


def load_agent_profile(state: ChatState) -> dict[str, Any]:
    return {
        "agent_profile": get_profile_service().ensure_agent_profile(
            state["db"], state["user_id"], state["agent_key"]
        )
    }


def retrieve_memory(state: ChatState) -> dict[str, Any]:
    if not state["scope"].in_scope:
        return {"memories": []}
    memories = get_personalization_engine().retrieve_memories(
        state["db"],
        user_id=state["user_id"],
        agent_key=state["agent_key"],
        request=state["request"],
    )
    return {"memories": memories}


def build_context(state: ChatState) -> dict[str, Any]:
    context = get_personalization_engine().build(
        state["db"],
        user=state["user"],
        agent_key=state["agent_key"],
        request=state["request"],
        global_profile=state["global_profile"],
        domain_profile=state.get("domain_profile"),
        agent_profile=state.get("agent_profile"),
        conversation_id=state.get("conversation_id"),
        attachment_name=state.get("attachment_name"),
        attachment_text=state.get("attachment_text"),
        memories=state.get("memories"),
    )
    return {"context": context}


def generate_response(state: ChatState) -> dict[str, Any]:
    spec = get_agent_spec(state["agent_key"])
    verdict: ScopeVerdict = state["scope"]

    # Out of scope: answer with a handoff instead of spending a model call.
    if not verdict.in_scope:
        content = handoff_message(spec, verdict)
        return {
            "result": AgentResult(
                content=content,
                output_kind="text",
                llm_response=LLMResponse(
                    content=content, model="scope-guard", provider="scope-guard"
                ),
                incomplete_reason="out_of_scope",
            )
        }

    agent = get_agent(state["agent_key"])
    try:
        return {"result": agent.run(state["context"])}
    except LLMProviderError:
        logger.error("Generation failed for %s", state["agent_key"])
        raise


def store_message(state: ChatState) -> dict[str, Any]:
    db: Session = state["db"]
    conversations = get_conversation_service()
    profiles = get_profile_service()
    memory_service = get_memory_service()

    spec = get_agent_spec(state["agent_key"])
    routing: RoutingDecision = state["routing"]
    result: AgentResult = state["result"]
    context: PersonalizedContext | None = state.get("context")
    verdict: ScopeVerdict = state["scope"]

    conversation = state.get("conversation")
    if conversation is None:
        conversation = conversations.create(
            db,
            user_id=state["user_id"],
            agent_key=spec.key,
            title=derive_title(state["request"], spec.key),
            commit=False,
        )
    elif conversation.message_count == 0 or conversation.title == "New conversation":
        conversation.title = derive_title(state["request"], conversation.agent_key)

    user_message = conversations.add_message(
        db,
        conversation=conversation,
        role="user",
        content=state["request"],
        meta={
            "attachment_name": state.get("attachment_name"),
            "attachment_chars": len(state.get("attachment_text") or "") or None,
        },
    )

    response = result.llm_response
    assistant_message = conversations.add_message(
        db,
        conversation=conversation,
        role="assistant",
        content=result.content,
        agent_key=spec.key,
        output_kind=result.output_kind,
        media=result.media_payload,
        meta={
            "routing": {
                "agent_key": routing.agent_key,
                "source": routing.source,
                "confidence": routing.confidence,
                "reason": routing.reason,
            },
            "provider": response.provider,
            "model": response.model,
            "usage": response.usage,
            "memories_used": [str(s.memory.id) for s in (context.memories if context else [])],
            "context_characters": context.context_characters if context else 0,
            "out_of_scope": not verdict.in_scope,
            "suggested_agent": verdict.suggested_key,
            "incomplete_reason": result.incomplete_reason,
        },
    )

    created: list[str] = []
    if verdict.in_scope:
        memories = memory_service.capture_from_message(
            db,
            user_id=state["user_id"],
            agent_key=spec.key,
            domain=spec.domain,
            message=state["request"],
            conversation_id=conversation.id,
            message_id=user_message.id,
        )
        created = [memory.content for memory in memories]

        agent_profile = state.get("agent_profile")
        if agent_profile is not None:
            profiles.record_interaction(
                db, agent_profile, topic=derive_title(state["request"], spec.key)
            )

    db.commit()
    for obj in (conversation, user_message, assistant_message):
        db.refresh(obj)

    started_at = state.get("started_at") or time.perf_counter()
    return {
        "conversation": conversation,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "new_memories": created,
        "latency_ms": int((time.perf_counter() - started_at) * 1000),
    }


# ------------------------------------------------------------------- assembly
CHAT_GRAPH_NODES = (
    "load_user",
    "router",
    "scope_guard",
    "load_global_profile",
    "load_domain_profile",
    "load_agent_profile",
    "retrieve_memory",
    "build_context",
    "generate_response",
    "store_message",
)

#: Nodes that run before generation — shared with the streaming path so there is
#: exactly one implementation of each step.
PREPARE_NODES = (
    load_user,
    router,
    scope_guard,
    load_global_profile,
    load_domain_profile,
    load_agent_profile,
    retrieve_memory,
    build_context,
)


def build_chat_graph() -> Any:
    graph = StateGraph(ChatState)
    for name, node in zip(CHAT_GRAPH_NODES, (*PREPARE_NODES, generate_response, store_message)):
        graph.add_node(name, node)

    graph.add_edge(START, CHAT_GRAPH_NODES[0])
    for previous, nxt in zip(CHAT_GRAPH_NODES, CHAT_GRAPH_NODES[1:]):
        graph.add_edge(previous, nxt)
    graph.add_edge(CHAT_GRAPH_NODES[-1], END)
    return graph.compile()


_chat_graph: Any | None = None


def get_chat_graph() -> Any:
    global _chat_graph
    if _chat_graph is None:
        _chat_graph = build_chat_graph()
        logger.info("Chat graph compiled: %s", " → ".join(CHAT_GRAPH_NODES))
    return _chat_graph


def _initial_state(
    db: Session,
    *,
    user_id: uuid.UUID,
    request: str,
    explicit_agent: str | None,
    conversation_id: uuid.UUID | None,
    attachment_name: str | None,
    attachment_text: str | None,
) -> ChatState:
    return {
        "db": db,
        "user_id": user_id,
        "request": request,
        "explicit_agent": explicit_agent,
        "conversation_id": conversation_id,
        "attachment_name": attachment_name,
        "attachment_text": attachment_text,
        "user": None,
        "global_profile": None,
        "domain_profile": None,
        "agent_profile": None,
        "conversation": None,
        "routing": None,
        "agent_key": None,
        "scope": None,
        "memories": None,
        "context": None,
        "result": None,
        "user_message": None,
        "assistant_message": None,
        "new_memories": None,
        "started_at": None,
        "latency_ms": None,
    }


def prepare_chat_turn(
    db: Session,
    *,
    user_id: uuid.UUID,
    request: str,
    explicit_agent: str | None = None,
    conversation_id: uuid.UUID | None = None,
    attachment_name: str | None = None,
    attachment_text: str | None = None,
) -> ChatState:
    """Run every node up to (not including) generation — used by streaming, so the
    routing decision and personalization trace can be sent before the first token."""
    state = _initial_state(
        db,
        user_id=user_id,
        request=request,
        explicit_agent=explicit_agent,
        conversation_id=conversation_id,
        attachment_name=attachment_name,
        attachment_text=attachment_text,
    )
    for node in PREPARE_NODES:
        state.update(node(state))  # type: ignore[typeddict-item]
    return state


def finalize_chat_turn(state: ChatState, result: AgentResult) -> ChatState:
    """Persist a streamed turn through the same ``store_message`` node."""
    state["result"] = result
    state.update(store_message(state))  # type: ignore[typeddict-item]
    return state


def run_chat_pipeline(
    db: Session,
    *,
    user_id: uuid.UUID,
    request: str,
    explicit_agent: str | None = None,
    conversation_id: uuid.UUID | None = None,
    attachment_name: str | None = None,
    attachment_text: str | None = None,
) -> ChatState:
    """Execute the compiled graph for one chat turn."""
    initial = _initial_state(
        db,
        user_id=user_id,
        request=request,
        explicit_agent=explicit_agent,
        conversation_id=conversation_id,
        attachment_name=attachment_name,
        attachment_text=attachment_text,
    )
    return get_chat_graph().invoke(initial)  # type: ignore[return-value]
