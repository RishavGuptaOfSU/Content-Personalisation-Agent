"""Registration and authentication."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.services.profile_service import get_profile_service

logger = get_logger(__name__)


class EmailAlreadyRegistered(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class UserService:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(func.lower(User.email) == email.strip().lower()))

    def register(self, db: Session, *, name: str, email: str, password: str) -> User:
        normalized_email = email.strip().lower()
        if self.get_by_email(db, normalized_email) is not None:
            raise EmailAlreadyRegistered(normalized_email)

        user = User(
            name=name.strip(),
            email=normalized_email,
            password_hash=hash_password(password),
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise EmailAlreadyRegistered(normalized_email) from exc
        db.refresh(user)

        # Every user starts with a global profile so personalization always has
        # a baseline to work from.
        get_profile_service().get_or_create_global_profile(db, user)
        logger.info("Registered user %s", user.email)
        return user

    def authenticate(self, db: Session, *, email: str, password: str) -> User:
        user = self.get_by_email(db, email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentials
        if not user.is_active:
            raise InvalidCredentials
        user.last_login_at = datetime.now(UTC)
        db.commit()
        db.refresh(user)
        return user

    def change_password(
        self, db: Session, *, user: User, current_password: str, new_password: str
    ) -> User:
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentials
        user.password_hash = hash_password(new_password)
        db.commit()
        db.refresh(user)
        return user


_service: UserService | None = None


def get_user_service() -> UserService:
    global _service
    if _service is None:
        _service = UserService()
    return _service
