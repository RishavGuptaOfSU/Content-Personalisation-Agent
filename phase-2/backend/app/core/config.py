"""Application configuration.

All configuration is environment driven (see ``.env.example``). Nothing secret is
ever hard-coded, and no provider credential is ever sent to the frontend.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------ app
    APP_NAME: str = "Content Personalization Agent"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ------------------------------------------------------------- database
    # Primary target: PostgreSQL + pgvector.
    #   postgresql+psycopg://user:pass@localhost:5432/content_personalization
    # A SQLite URL is accepted as a zero-dependency development fallback; the
    # vector store transparently degrades to in-process cosine similarity.
    DATABASE_URL: str = "postgresql+psycopg://cpa:cpa@localhost:5432/content_personalization"
    SQL_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ------------------------------------------------------------- security
    JWT_SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    BCRYPT_ROUNDS: int = 12

    # ----------------------------------------------------------------- cors
    # ``NoDecode`` keeps pydantic-settings from JSON-decoding the raw env value,
    # so a plain comma-separated list works in .env as well as a JSON array.
    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://localhost:3000",
        ]
    )

    # ------------------------------------------------------------------ llm
    #   "ollama"  -> local models via Ollama (no API key, no cloud)
    #   "openai"  -> any OpenAI-compatible endpoint (OpenAI, Groq, LM Studio, vLLM…)
    #   "bedrock" -> AWS Bedrock
    #   "mock"    -> deterministic local composer; runs with no model at all
    LLM_PROVIDER: Literal["ollama", "openai", "bedrock", "mock"] = "mock"
    # Reasoning models (nemotron-3-*, beam, gpt-oss with a high effort setting)
    # spend completion tokens on hidden thinking before they answer. Measured on
    # Ollama Cloud: a 17-word sentence cost nemotron-3-super 84 completion
    # tokens against ~25 for a non-reasoning model. When the budget runs out
    # mid-thought the API returns HTTP 200 with an empty message and
    # finish_reason "length" — a reply that looks like a provider outage but is
    # really a budget problem, and an intermittent one.
    #: Whether image attachments may be sent to the model.
    #:   "auto" -> allow when the model name matches a known multimodal family
    #:   "on"   -> always allow (use for a multimodal model we do not recognise)
    #:   "off"  -> refuse image uploads
    #: An OpenAI-compatible API has no capability endpoint, so "auto" is a
    #: name-pattern guess; see app/llm/vision.py for what was measured.
    LLM_VISION: Literal["auto", "on", "off"] = "auto"
    #: Retry once with more headroom when that exact signature appears.
    LLM_EMPTY_REPLY_RETRY: bool = True
    #: How much headroom the retry gets, as a multiple of the original budget.
    LLM_EMPTY_REPLY_BUDGET_MULTIPLIER: float = 3.0
    #: Hard ceiling for the retry, so a pathological model cannot bill forever.
    LLM_MAX_TOKENS_CEILING: int = 4000
    #: Per-agent model overrides, so a single agent can be pointed at a
    #: different model without a code change:
    #:   AGENT_MODELS=marketing.campaign-planner=glm-5.3,marketing.post-image=gpt-oss:20b
    #: Deployment wins over code: these take precedence over an agent's
    #: ``options["model"]`` in the catalog. An empty value (the default) means
    #: every agent uses the provider default.
    AGENT_MODELS: Annotated[dict[str, str], NoDecode] = Field(default_factory=dict)
    LLM_TEMPERATURE: float = 0.4
    LLM_MAX_TOKENS: int = 1600
    ROUTER_TEMPERATURE: float = 0.0
    ROUTER_MAX_TOKENS: int = 256

    # ----------------------------------------------------------------- ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    #: Small, fast model for the routing classification step.
    OLLAMA_ROUTER_MODEL: str = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    #: Local models on CPU are slow; this must exceed the slowest expected reply.
    OLLAMA_TIMEOUT: float = 600.0
    OLLAMA_NUM_CTX: int = 8192
    #: How long Ollama keeps the model resident (avoids a reload per request).
    OLLAMA_KEEP_ALIVE: str = "10m"

    # ------------------------------------------------- openai-compatible api
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_ROUTER_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_TIMEOUT: float = 180.0

    # AWS / Bedrock
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_SESSION_TOKEN: str | None = None
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    BEDROCK_ROUTER_MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"
    BEDROCK_EMBEDDING_MODEL_ID: str = "amazon.titan-embed-text-v2:0"

    # ---------------------------------------------------------------- media
    # Visual agents (post images, ad creatives, posters, charts).
    #   "local"  -> typographic cards rendered with Pillow; no key, works offline
    #   "openai" -> hosted image generation via an OpenAI-compatible images API
    IMAGE_PROVIDER: Literal["local", "openai"] = "local"
    OPENAI_IMAGE_MODEL: str = "gpt-image-1"
    OPENAI_IMAGE_TIMEOUT: float = 180.0
    #: Where generated files are written (relative paths resolve inside backend/).
    MEDIA_ROOT: str = "generated_media"
    #: Oldest files beyond this count are pruned after each render.
    MEDIA_MAX_FILES: int = 400

    # --------------------------------------------------------------- memory
    #   "ollama" -> nomic-embed-text etc. (real embeddings, local)
    #   "openai" -> text-embedding-3-small etc.
    #   "local"  -> deterministic hashing embedder, no model required
    EMBEDDING_PROVIDER: Literal["ollama", "openai", "bedrock", "local"] = "local"
    EMBEDDING_DIM: int = 1024
    MEMORY_TOP_K: int = 6
    MEMORY_MIN_SIMILARITY: float = 0.25
    MEMORY_MAX_PER_AGENT: int = 300
    SHORT_TERM_WINDOW: int = 12  # recent messages injected into the prompt
    # Prompt evaluation is the dominant latency on CPU-only hardware, and replayed
    # history is usually the largest part of the prompt. These cap the *size* of
    # the short-term window, not just the message count: without them a couple of
    # long code-heavy answers can turn a two-character message into a
    # 2000-token prompt.
    SHORT_TERM_MAX_CHARS: int = 3000
    SHORT_TERM_MESSAGE_MAX_CHARS: int = 900
    #: A greeting needs continuity, not the whole previous answer replayed.
    SHORT_TERM_TRIVIAL_MAX_CHARS: int = 700
    # Reply budget for trivial turns ("hi", "thanks") — a greeting does not need
    # the full LLM_MAX_TOKENS allowance.
    TRIVIAL_REPLY_MAX_TOKENS: int = 160

    # Hybrid retrieval: standing preferences ("always keep posts short") must
    # apply to every request for that agent, not only to topically similar ones,
    # so they are pinned into the context alongside the semantic matches.
    MEMORY_STANDING_LIMIT: int = 4
    MEMORY_STANDING_IMPORTANCE: float = 0.6

    # ------------------------------------------------------- personalization
    FEEDBACK_PROMOTION_THRESHOLD: int = 2  # repeats before a profile update
    MEMORY_DEDUPE_SIMILARITY: float = 0.92

    # ----------------------------------------------------------- scope guard
    # Agents are narrow; a request that clearly belongs elsewhere is handed off
    # instead of half-answered. Deliberately conservative — a wrong handoff is
    # worse than a slightly off-topic answer.
    #: Requests shorter than this are never handed off (greetings, "thanks").
    SCOPE_MIN_REQUEST_CHARS: int = 15
    #: The selected agent must score at or below this to be considered unrelated.
    SCOPE_OWN_MAX_SCORE: float = 1.5
    #: The alternative agent must score at least this much.
    SCOPE_OTHER_MIN_SCORE: float = 4.0
    #: And beat the selected agent by at least this margin.
    SCOPE_MIN_MARGIN: float = 3.0

    # -------------------------------------------------------- cost / latency
    # Each of these adds an extra model call per message. With a local CPU model
    # that is the difference between a 15s and a 45s reply, so both are tunable.
    #: Use the LLM to classify intent when no agent was explicitly selected.
    ROUTER_USE_LLM: bool = True
    #: Skip the LLM router when the keyword router already has a clear winner
    #: (best score minus runner-up >= this margin). Set 0 to always ask the LLM.
    ROUTER_LLM_MIN_MARGIN: float = 3.0
    #: A keyword winner must also clear this absolute score to skip the LLM.
    ROUTER_KEYWORD_MIN_SCORE: float = 4.0
    #: Ask the LLM to extract durable memories on top of the rule-based
    #: extractor. Off by default: the rules cover the common cases for free.
    MEMORY_LLM_EXTRACTION: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, value: Any) -> Any:
        """Accept ``a,b,c`` or ``["a","b"]`` or an actual list."""
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                import json

                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @field_validator("AGENT_MODELS", mode="before")
    @classmethod
    def _parse_agent_models(cls, value: Any) -> Any:
        """Accept ``agent.key=model,other.key=model`` as well as a JSON object.

        Model names contain colons (``gpt-oss:20b``) but never ``=``, so the
        first ``=`` is the separator. A malformed entry raises rather than being
        dropped: silently ignoring a pin would make an eval run look like it
        used a model it never touched.
        """
        if not isinstance(value, str):
            return value
        stripped = value.strip()
        if not stripped:
            return {}
        if stripped.startswith("{"):
            import json

            return json.loads(stripped)
        pairs: dict[str, str] = {}
        for entry in stripped.split(","):
            entry = entry.strip()
            if not entry:
                continue
            if "=" not in entry:
                raise ValueError(
                    f"AGENT_MODELS entry {entry!r} is not of the form "
                    "<domain>.<agent>=<model>"
                )
            key, model = entry.split("=", 1)
            key, model = key.strip().lower(), model.strip()
            if not key or not model:
                raise ValueError(
                    f"AGENT_MODELS entry {entry!r} has an empty agent key or model"
                )
            pairs[key] = model
        return pairs

    # ------------------------------------------------------------- helpers
    @property
    def is_postgres(self) -> bool:
        return self.DATABASE_URL.startswith("postgres")

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def bedrock_credentials_present(self) -> bool:
        return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY)

    @property
    def uses_real_llm(self) -> bool:
        """True when an actual model serves requests (i.e. not the local composer)."""
        return self.LLM_PROVIDER != "mock"

    @property
    def router_model(self) -> str | None:
        """Provider-specific model id for the cheap routing step."""
        return {
            "ollama": self.OLLAMA_ROUTER_MODEL,
            "openai": self.OPENAI_ROUTER_MODEL,
            "bedrock": self.BEDROCK_ROUTER_MODEL_ID,
        }.get(self.LLM_PROVIDER)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
