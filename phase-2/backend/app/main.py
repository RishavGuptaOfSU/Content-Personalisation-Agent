"""FastAPI application entry point."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import __version__
from app.api import api_router
from app.core.config import settings
from app.core.http import HTTP_422_UNPROCESSABLE
from app.core.logging import configure_logging, get_logger
from app.database.session import engine, init_db
from app.llm.registry import provider_status

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s v%s (%s)", settings.APP_NAME, __version__, settings.APP_ENV)
    init_db()
    status_payload = provider_status()
    logger.info(
        "LLM provider=%s model=%s | embeddings=%s",
        status_payload["llm"].get("provider"),
        status_payload["llm"].get("model"),
        status_payload["embeddings"].get("provider"),
    )
    if settings.LLM_PROVIDER == "mock":
        logger.warning(
            "LLM_PROVIDER=mock — using the local development provider, not a real model. "
            "For real answers set LLM_PROVIDER=ollama (local, free: `ollama pull llama3.2:3b`), "
            "or openai / bedrock. See backend/.env.example."
        )
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    description=(
        "Multi-agent AI personalization platform: 7 specialized agents, a global user "
        "profile, per-agent profiles, semantic long-term memory (pgvector) and a "
        "feedback-driven personalization loop."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    max_age=600,
)


@app.middleware("http")
async def add_timing_header(request: Request, call_next):  # type: ignore[no-untyped-def]
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - started) * 1000:.1f}"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Flatten pydantic errors into a message the UI can show in a toast."""
    details = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ()) if part != "body")
        details.append(f"{location}: {error.get('msg')}" if location else str(error.get("msg")))
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE,
        content={"detail": "; ".join(details) or "Invalid request", "errors": exc.errors()},
    )


app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["meta"])
def root() -> dict[str, object]:
    return {
        "name": settings.APP_NAME,
        "version": __version__,
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX,
    }


@app.get("/health", tags=["meta"])
def health() -> dict[str, object]:
    database_ok = True
    database_error: str | None = None
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        database_ok = False
        database_error = str(exc)

    from app.memory.vector_store import get_vector_store

    return {
        "status": "ok" if database_ok else "degraded",
        "version": __version__,
        "environment": settings.APP_ENV,
        "database": {
            "ok": database_ok,
            "dialect": engine.dialect.name,
            "vector_store": get_vector_store().name,
            "error": database_error,
        },
        "providers": provider_status(),
    }
