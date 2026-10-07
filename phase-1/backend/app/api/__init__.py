"""API layer."""

from fastapi import APIRouter

from app.api.routes import (
    auth,
    catalog,
    chat,
    conversations,
    dashboard,
    feedback,
    media,
    memory,
    profiles,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(catalog.router)
api_router.include_router(profiles.router)
api_router.include_router(chat.router)
api_router.include_router(conversations.router)
api_router.include_router(feedback.router)
api_router.include_router(memory.router)
api_router.include_router(dashboard.router)
api_router.include_router(media.router)

__all__ = ["api_router"]
