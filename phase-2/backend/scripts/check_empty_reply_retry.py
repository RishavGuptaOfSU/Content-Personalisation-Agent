#!/usr/bin/env python
"""Checks the empty-reply retry for reasoning models — no network.

The free reasoning models on Ollama Cloud (nemotron-3-*, beam) spend completion
tokens on hidden thinking before answering. When the budget runs out mid-thought
the API returns **HTTP 200 with an empty message** and ``finish_reason:
"length"``. Measured on nemotron-3-nano:30b: 1 request in 6 came back with 700
completion tokens and zero characters of content.

That used to surface as "the language model provider is unavailable" — a
provider outage message for what is really a token budget problem. It also made
eval runs non-comparable, because a different number of cases errored each time
(4 to 19 of 30 depending on the model).

This asserts the retry fires on exactly that signature and nowhere else.

    python scripts/check_empty_reply_retry.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402

from app.llm.base import ChatMessage, LLMProviderError  # noqa: E402
from app.llm.openai_compatible import OpenAICompatibleLLMProvider  # noqa: E402

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" -> {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


def reply(
    content: str | None,
    *,
    finish_reason: str = "stop",
    reasoning: str | None = None,
    completion_tokens: int = 50,
) -> dict[str, Any]:
    message: dict[str, Any] = {"role": "assistant", "content": content}
    if reasoning is not None:
        message["reasoning"] = reasoning
    return {
        "id": "chatcmpl-test",
        "model": "test-model",
        "choices": [{"message": message, "finish_reason": finish_reason}],
        "usage": {"prompt_tokens": 100, "completion_tokens": completion_tokens},
    }


class Transport(httpx.BaseTransport):
    """Serves queued JSON bodies and records the max_tokens asked for."""

    def __init__(self, bodies: list[dict[str, Any]], status: int = 200) -> None:
        self.bodies = list(bodies)
        self.status = status
        self.budgets: list[int] = []
        self.calls = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1
        payload = json.loads(request.content)
        self.budgets.append(payload["max_tokens"])
        body = self.bodies.pop(0) if self.bodies else self.bodies_default()
        return httpx.Response(self.status, json=body, request=request)

    def bodies_default(self) -> dict[str, Any]:
        return reply("fallback")


#: Captured once, before any patching, so re-patching cannot wrap the fake in
#: itself — the provider resolves ``httpx.Client`` through the shared httpx
#: module, so the patch is global while it is installed.
REAL_CLIENT = httpx.Client


def provider_with(transport: Transport) -> OpenAICompatibleLLMProvider:
    """A provider whose httpx.Client is bound to the fake transport."""
    instance = OpenAICompatibleLLMProvider(model="test-model")

    def client_factory(*args: Any, **kwargs: Any) -> httpx.Client:
        kwargs.pop("timeout", None)
        return REAL_CLIENT(transport=transport, timeout=5.0)

    httpx.Client = client_factory  # type: ignore[assignment]
    return instance


def restore() -> None:
    httpx.Client = REAL_CLIENT  # type: ignore[assignment]


MESSAGES = [ChatMessage(role="user", content="Write a LinkedIn post")]


def main() -> int:
    from app.core.config import settings

    settings.LLM_MAX_TOKENS = 700
    settings.LLM_EMPTY_REPLY_RETRY = True
    settings.LLM_EMPTY_REPLY_BUDGET_MULTIPLIER = 3.0
    settings.LLM_MAX_TOKENS_CEILING = 4000

    try:
        print("1. a normal reply is returned on the first call")
        transport = Transport([reply("Here is your post.")])
        result = provider_with(transport).generate(MESSAGES, max_tokens=700)
        check("content came back", result.content == "Here is your post.")
        check("only one call was made", transport.calls == 1, str(transport.calls))
        check("the budget was not inflated", transport.budgets == [700], str(transport.budgets))

        print("\n2. empty + finish_reason 'length' retries with headroom")
        transport = Transport(
            [
                reply("", finish_reason="length", completion_tokens=700),
                reply("Recovered post.", completion_tokens=300),
            ]
        )
        result = provider_with(transport).generate(MESSAGES, max_tokens=700)
        check("the retry recovered the answer", result.content == "Recovered post.")
        check("exactly two calls were made", transport.calls == 2, str(transport.calls))
        check(
            "the retry tripled the budget",
            transport.budgets == [700, 2100],
            str(transport.budgets),
        )
        check(
            "both budgets are recorded on the response",
            result.raw.get("token_budgets") == [700, 2100],
            str(result.raw.get("token_budgets")),
        )

        print("\n3. a null content with hidden reasoning also retries")
        transport = Transport(
            [
                reply(None, finish_reason="length", reasoning="Let me think about this..."),
                reply("Second attempt."),
            ]
        )
        result = provider_with(transport).generate(MESSAGES, max_tokens=700)
        check("null content is treated as empty", result.content == "Second attempt.")
        check("it retried", transport.calls == 2, str(transport.calls))

        # The reasoning field alone is enough: some gateways report "stop" even
        # though only thinking was produced.
        transport = Transport(
            [
                reply("   ", finish_reason="stop", reasoning="thinking hard"),
                reply("Third attempt."),
            ]
        )
        result = provider_with(transport).generate(MESSAGES, max_tokens=700)
        check(
            "reasoning with no answer retries even on finish_reason 'stop'",
            result.content == "Third attempt." and transport.calls == 2,
            f"calls={transport.calls}",
        )

        print("\n4. an empty reply that is NOT a budget problem fails fast")
        transport = Transport([reply("", finish_reason="stop")])
        try:
            provider_with(transport).generate(MESSAGES, max_tokens=700)
        except LLMProviderError as exc:
            check("it raises", True)
            check("it does not retry blindly", transport.calls == 1, str(transport.calls))
            check(
                "the message names the model and the finish reason",
                "test-model" in str(exc) and "stop" in str(exc),
                str(exc)[:90],
            )
        else:
            check("it raises", False, "returned a result for an empty reply")

        print("\n5. the retry is bounded")
        transport = Transport([reply("", finish_reason="length")] * 6)
        try:
            provider_with(transport).generate(MESSAGES, max_tokens=700)
        except LLMProviderError as exc:
            check("a model that never answers still terminates", True)
            check(
                "it stops at the ceiling",
                max(transport.budgets) <= settings.LLM_MAX_TOKENS_CEILING,
                str(transport.budgets),
            )
            check(
                "it did not loop forever",
                transport.calls <= 4,
                f"{transport.calls} calls, budgets {transport.budgets}",
            )
            check("the error explains the cause", "budget" in str(exc) or "max_tokens" in str(exc))
        else:
            check("a model that never answers still terminates", False, "no error raised")

        # Already at the ceiling: there is no headroom to give, so one call only.
        transport = Transport([reply("", finish_reason="length")])
        try:
            provider_with(transport).generate(MESSAGES, max_tokens=4000)
        except LLMProviderError:
            check("at the ceiling it does not retry", transport.calls == 1, str(transport.calls))
        else:
            check("at the ceiling it does not retry", False)

        print("\n6. the retry can be switched off")
        settings.LLM_EMPTY_REPLY_RETRY = False
        transport = Transport([reply("", finish_reason="length"), reply("unused")])
        try:
            provider_with(transport).generate(MESSAGES, max_tokens=700)
        except LLMProviderError:
            check(
                "LLM_EMPTY_REPLY_RETRY=false means a single call",
                transport.calls == 1,
                str(transport.calls),
            )
        else:
            check("LLM_EMPTY_REPLY_RETRY=false means a single call", False)
        settings.LLM_EMPTY_REPLY_RETRY = True

        print("\n7. a real provider error is still a provider error")
        transport = Transport([{"error": {"message": "nope"}}], status=500)
        try:
            provider_with(transport).generate(MESSAGES, max_tokens=700)
        except LLMProviderError as exc:
            check("HTTP 500 raises", "500" in str(exc), str(exc)[:70])
            check("it is not retried as a budget problem", transport.calls == 1)
        else:
            check("HTTP 500 raises", False)

        transport = Transport([{"choices": []}])
        try:
            provider_with(transport).generate(MESSAGES, max_tokens=700)
        except LLMProviderError as exc:
            check("no choices raises", "no choices" in str(exc).lower(), str(exc)[:60])
        else:
            check("no choices raises", False)
    finally:
        restore()

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): " + "; ".join(FAILURES))
        return 1
    print("ALL EMPTY-REPLY RETRY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
