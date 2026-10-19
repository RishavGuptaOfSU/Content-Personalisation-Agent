#!/usr/bin/env python
"""Checks for the per-agent model override — no network, no database.

An agent can pin its own model via ``options["model"]`` in the catalog. This
asserts the plumbing works in both directions: unset means "use the provider
default" (so nothing changes for agents that do not opt in), and set means the
name is actually handed to the provider on every call, including streaming.

    python scripts/check_agent_models.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.catalog import AGENTS, list_agents  # noqa: E402
from app.agents.runtime import get_agent  # noqa: E402
from app.agents.schema import AgentSpec  # noqa: E402

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" -> {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


class RecordingProvider:
    """Captures what the runtime asks for, without calling anything."""

    name = "recording"

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def generate(self, messages, **kwargs):  # noqa: ANN001, ANN003
        self.calls.append(kwargs)
        raise _Captured

    def stream(self, messages, **kwargs):  # noqa: ANN001, ANN003
        self.calls.append(kwargs)
        raise _Captured


class _Captured(Exception):
    """Raised to stop the agent as soon as the provider call is observed."""


def observed_model(spec: AgentSpec, *, streaming: bool = False) -> tuple[bool, Any]:
    """The `model` kwarg the runtime passes for this agent."""
    import app.agents.runtime as runtime

    recorder = RecordingProvider()
    original = runtime.get_llm_provider
    runtime.get_llm_provider = lambda: recorder  # type: ignore[assignment]
    try:
        agent = get_agent(spec.key)
        context = _stub_context(spec)
        try:
            if streaming:
                list(agent.stream(context))
            else:
                agent.run(context)
        except _Captured:
            pass
    finally:
        runtime.get_llm_provider = original  # type: ignore[assignment]

    if not recorder.calls:
        return False, None
    return True, recorder.calls[-1].get("model")


def _stub_context(spec: AgentSpec):
    """A minimal PersonalizedContext — enough to reach the provider call."""
    from app.services.personalization import PersonalizedContext

    return PersonalizedContext(
        agent_key=spec.key,
        agent_spec=spec,
        system_prompt="=== USER OUTPUT CONTRACT ===\n- test",
        context_block="",
        short_term=[],
        memories=[],
        hints={"request": "Write something about our brand", "agent_key": spec.key},
        user_request="Write something about our brand",
    )


def main() -> int:
    print("1. by default no agent pins a model (the provider default is used)")
    for spec in list_agents():
        check(
            f"{spec.key} declares no model override",
            spec.options.get("model") in (None, ""),
            str(spec.options.get("model")),
        )

    print("\n2. the runtime passes model=None when nothing is pinned")
    for spec in list_agents():
        called, model = observed_model(spec)
        check(f"{spec.key} reached the provider", called)
        check(f"{spec.key} passed model=None", model is None, repr(model))

    print("\n3. pinning a model sends that exact name")
    spec = AGENTS["marketing.campaign-planner"]
    original_options = spec.options
    try:
        object.__setattr__(spec, "options", {**original_options, "model": "deepseek-v4-pro"})
        # The runtime caches instances, so clear it to pick the change up.
        import app.agents.runtime as runtime

        runtime._instances.clear()
        called, model = observed_model(spec)
        check("pinned agent reached the provider", called)
        check("the pinned name was passed", model == "deepseek-v4-pro", repr(model))
        check(
            "BaseAgent.model() reports it",
            get_agent(spec.key).model() == "deepseek-v4-pro",
            str(get_agent(spec.key).model()),
        )
    finally:
        object.__setattr__(spec, "options", original_options)
        import app.agents.runtime as runtime

        runtime._instances.clear()

    print("\n4. streaming honours the override too")
    text_spec = AGENTS["marketing.social-copy"]
    original_options = text_spec.options
    try:
        object.__setattr__(text_spec, "options", {**original_options, "model": "glm-5.3-flash"})
        import app.agents.runtime as runtime

        runtime._instances.clear()
        called, model = observed_model(text_spec, streaming=True)
        check("streaming reached the provider", called)
        check("streaming passed the pinned name", model == "glm-5.3-flash", repr(model))
    finally:
        object.__setattr__(text_spec, "options", original_options)
        import app.agents.runtime as runtime

        runtime._instances.clear()

    print("\n5. AGENT_MODELS parses the env form")
    from app.core.config import Settings

    parsed = Settings(
        AGENT_MODELS="marketing.campaign-planner=glm-5.3,marketing.post-image=gpt-oss:20b"
    ).AGENT_MODELS
    check(
        "two entries parsed",
        parsed
        == {
            "marketing.campaign-planner": "glm-5.3",
            "marketing.post-image": "gpt-oss:20b",
        },
        repr(parsed),
    )
    check("a colon in the model name survives", parsed.get("marketing.post-image") == "gpt-oss:20b")
    check("an empty value means no overrides", Settings(AGENT_MODELS="").AGENT_MODELS == {})
    for bad in ("marketing.campaign-planner", "=glm-5.3", "marketing.seo-optimizer="):
        try:
            Settings(AGENT_MODELS=bad)
        except Exception:
            check(f"malformed entry {bad!r} is rejected", True)
        else:
            check(f"malformed entry {bad!r} is rejected", False)

    print("\n6. an env override reaches the provider and beats the catalog")
    from app.core import config as config_module
    import app.agents.runtime as runtime

    planner = AGENTS["marketing.campaign-planner"]
    original_options = planner.options
    original_agent_models = runtime.settings.AGENT_MODELS
    try:
        runtime.settings.AGENT_MODELS = {"marketing.campaign-planner": "kimi-k3"}
        runtime._instances.clear()
        called, model = observed_model(planner)
        check("env-pinned agent reached the provider", called)
        check("the env name was passed", model == "kimi-k3", repr(model))
        check(
            "an agent with no env entry is unaffected",
            get_agent("marketing.social-copy").model() is None,
            str(get_agent("marketing.social-copy").model()),
        )

        # Both set: the environment is deployment-level and must win.
        object.__setattr__(planner, "options", {**original_options, "model": "glm-5.2"})
        runtime._instances.clear()
        check(
            "env beats the catalog declaration",
            get_agent(planner.key).model() == "kimi-k3",
            str(get_agent(planner.key).model()),
        )
    finally:
        object.__setattr__(planner, "options", original_options)
        runtime.settings.AGENT_MODELS = original_agent_models
        runtime._instances.clear()
    check(
        "the default config pins nothing",
        config_module.settings.AGENT_MODELS == {},
        repr(config_module.settings.AGENT_MODELS),
    )

    print("\n7. the override is cleared again (no leakage between checks)")
    for spec in list_agents():
        check(f"{spec.key} back to no override", get_agent(spec.key).model() is None)

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): " + "; ".join(FAILURES))
        return 1
    print("ALL PER-AGENT MODEL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
