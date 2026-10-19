"""Authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token
from app.schemas.auth import (
    ChangePasswordRequest,
    TokenResponse,
    UserLogin,
    UserRead,
    UserRegister,
)
from app.services.user_service import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    get_user_service,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(user) -> TokenResponse:  # type: ignore[no-untyped-def]
    token, expires_in = create_access_token(user.id, extra_claims={"email": user.email})
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserRead.model_validate(user),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: DbSession) -> TokenResponse:
    """Create an account and return an access token (auto-login after signup)."""
    try:
        user = get_user_service().register(
            db, name=payload.name, email=payload.email, password=payload.password
        )
    except EmailAlreadyRegistered as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: DbSession) -> TokenResponse:
    try:
        user = get_user_service().authenticate(
            db, email=payload.email, password=payload.password
        )
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        ) from exc
    return _token_response(user)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.post("/change-password", response_model=UserRead)
def change_password(
    payload: ChangePasswordRequest, user: CurrentUser, db: DbSession
) -> UserRead:
    try:
        updated = get_user_service().change_password(
            db,
            user=user,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        ) from exc
    return UserRead.model_validate(updated)
