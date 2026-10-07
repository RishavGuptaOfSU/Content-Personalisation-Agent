"""AWS Bedrock provider (production LLM backend).

Uses ``langchain_aws.ChatBedrockConverse`` so the same code path works for
Anthropic Claude, Amazon Nova, Meta Llama and Mistral model ids on Bedrock.
Credentials are resolved by boto3 (env vars, shared config, or the instance/task
role) and never leave the backend.
"""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.base import (
    BaseEmbeddingProvider,
    BaseLLMProvider,
    ChatMessage,
    LLMProviderError,
    LLMResponse,
)

logger = get_logger(__name__)


def _boto_kwargs() -> dict[str, Any]:
    kwargs: dict[str, Any] = {"region_name": settings.AWS_REGION}
    if settings.bedrock_credentials_present:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
        if settings.AWS_SESSION_TOKEN:
            kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN
    return kwargs


class BedrockLLMProvider(BaseLLMProvider):
    name = "bedrock"

    def __init__(self, model_id: str | None = None) -> None:
        self._model_id = model_id or settings.BEDROCK_MODEL_ID
        self._clients: dict[tuple[str, float, int], Any] = {}

    @property
    def default_model(self) -> str:
        return self._model_id

    def _client(self, model: str, temperature: float, max_tokens: int) -> Any:
        key = (model, temperature, max_tokens)
        if key not in self._clients:
            try:
                from langchain_aws import ChatBedrockConverse
            except ImportError as exc:  # pragma: no cover
                raise LLMProviderError(
                    "langchain-aws is not installed; run pip install -r requirements.txt"
                ) from exc
            self._clients[key] = ChatBedrockConverse(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **_boto_kwargs(),
            )
        return self._clients[key]

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
        model_id = model or self._model_id
        client = self._client(
            model_id,
            settings.LLM_TEMPERATURE if temperature is None else temperature,
            max_tokens or settings.LLM_MAX_TOKENS,
        )

        payload: list[tuple[str, str]] = []
        if system:
            payload.append(("system", system))
        for message in messages:
            role = "ai" if message.role == "assistant" else message.role
            payload.append((role, message.content))

        try:
            result = client.invoke(payload)
        except Exception as exc:  # pragma: no cover - network dependent
            logger.exception("Bedrock invocation failed")
            raise LLMProviderError(f"Bedrock request failed: {exc}") from exc

        content = result.content
        if isinstance(content, list):  # converse API returns content blocks
            content = "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )

        usage = getattr(result, "usage_metadata", None) or {}
        return LLMResponse(
            content=str(content).strip(),
            model=model_id,
            provider=self.name,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            stop_reason=(result.response_metadata or {}).get("stopReason"),
            raw={"response_metadata": result.response_metadata or {}},
        )

    def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "model": self._model_id,
            "region": settings.AWS_REGION,
            "credentials_configured": settings.bedrock_credentials_present,
            "ok": True,
        }


class BedrockEmbeddingProvider(BaseEmbeddingProvider):
    name = "bedrock"

    def __init__(self, model_id: str | None = None, dimension: int | None = None) -> None:
        self._model_id = model_id or settings.BEDROCK_EMBEDDING_MODEL_ID
        self._dimension = dimension or settings.EMBEDDING_DIM
        self._client: Any | None = None

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from langchain_aws import BedrockEmbeddings
            except ImportError as exc:  # pragma: no cover
                raise LLMProviderError("langchain-aws is not installed") from exc
            self._client = BedrockEmbeddings(model_id=self._model_id, **_boto_kwargs())
        return self._client

    def embed(self, text: str) -> list[float]:
        try:
            vector = self._get_client().embed_query(text)
        except Exception as exc:  # pragma: no cover - network dependent
            raise LLMProviderError(f"Bedrock embedding failed: {exc}") from exc
        return [float(component) for component in vector]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        try:
            vectors = self._get_client().embed_documents(texts)
        except Exception as exc:  # pragma: no cover
            raise LLMProviderError(f"Bedrock embedding failed: {exc}") from exc
        return [[float(component) for component in vector] for vector in vectors]
