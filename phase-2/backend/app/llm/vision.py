"""Whether the configured model can actually look at an image.

This exists so the app can refuse an image upload *before* the user writes a
message around it. Accepting a PNG and then silently sending a text-only
request is the worst outcome: the reply looks plausible and is based on nothing.

How it knows
------------
There is no capability endpoint on an OpenAI-compatible API — you find out by
sending an image and reading the error. So this keeps a list of model families
known to be multimodal, matched on substrings because providers decorate names
with sizes and dates (``gemma4:31b``, ``gpt-4o-2024-08-06``).

Measured against Ollama Cloud on 2026-10-19 with a 240x120 PNG containing the
text "ACME CLOUD 42":

* ``gemma4:31b`` read the text back correctly
* ``gpt-oss:120b``, ``gpt-oss:20b``, ``beam``, ``nemotron-3-super`` and
  ``nemotron-3-ultra`` all returned "this model does not support image input"

A list like this goes stale, so ``LLM_VISION`` overrides it in both directions:
set it to ``on`` when running a multimodal model this does not recognise, and
``off`` to turn image uploads away regardless.
"""

from __future__ import annotations

from app.core.config import settings

#: Model-name substrings known to accept image input. Lowercase.
VISION_MODEL_PATTERNS: tuple[str, ...] = (
    # Measured on this project
    "gemma4",
    # Google
    "gemma3",
    "gemini",
    # OpenAI
    "gpt-4o",
    "gpt-4.1",
    "gpt-4-turbo",
    "gpt-5",
    "o3",
    "o4-mini",
    # Anthropic
    "claude-3",
    "claude-4",
    "claude-sonnet",
    "claude-opus",
    "claude-haiku",
    # Open multimodal families
    "llava",
    "llama3.2-vision",
    "llama-3.2-vision",
    "llama4",
    "qwen2-vl",
    "qwen2.5-vl",
    "qwen3-vl",
    "pixtral",
    "minicpm-v",
    "moondream",
    "internvl",
    "phi-3-vision",
    "phi-4-multimodal",
    # AWS
    "nova-lite",
    "nova-pro",
    "nova-premier",
)

#: Providers that can carry an image at all, whatever the model.
_VISION_CAPABLE_PROVIDERS = ("openai", "ollama", "bedrock")


def active_model() -> str:
    """The model id serving chat requests right now."""
    return {
        "ollama": settings.OLLAMA_MODEL,
        "openai": settings.OPENAI_MODEL,
        "bedrock": settings.BEDROCK_MODEL_ID,
        "mock": "local-dev-composer",
    }.get(settings.LLM_PROVIDER, "unknown")


def model_supports_vision(model: str | None) -> bool:
    """True when this model name matches a known multimodal family."""
    name = (model or "").lower()
    if not name:
        return False
    return any(pattern in name for pattern in VISION_MODEL_PATTERNS)


def vision_supported(model: str | None = None) -> bool:
    """Whether an image upload can be honoured as things are configured.

    ``LLM_VISION`` wins over detection, because the pattern list cannot know
    about every multimodal model that will ship after this was written.
    """
    setting = str(getattr(settings, "LLM_VISION", "auto")).strip().lower()
    if setting in {"off", "false", "0", "no"}:
        return False

    # The local composer has no model at all; it accepts images so the feature
    # can be exercised in development, and reports that it only sees metadata.
    if settings.LLM_PROVIDER == "mock":
        return setting in {"on", "true", "1", "yes"}

    if settings.LLM_PROVIDER not in _VISION_CAPABLE_PROVIDERS:
        return False
    if setting in {"on", "true", "1", "yes"}:
        return True
    return model_supports_vision(model or active_model())


def vision_status() -> dict[str, object]:
    """Reported by ``/chat/pipeline`` so the UI can explain itself."""
    model = active_model()
    return {
        "model": model,
        "supported": vision_supported(model),
        "detected": model_supports_vision(model),
        "setting": str(getattr(settings, "LLM_VISION", "auto")),
        "reason": (
            f"{model} matches a known multimodal family"
            if model_supports_vision(model)
            else f"{model} is not a known multimodal model; set LLM_VISION=on to override"
        ),
    }


__all__ = [
    "VISION_MODEL_PATTERNS",
    "active_model",
    "model_supports_vision",
    "vision_status",
    "vision_supported",
]
