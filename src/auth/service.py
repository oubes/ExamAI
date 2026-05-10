# ---- imports ---- #
from datetime import datetime, timedelta, timezone
import logging
from uuid import UUID
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import create_access_token, create_refresh_token
from src.auth.password import hash_password, verify_password
from src.auth.email_token import (
    create_password_reset_token,
    decode_password_reset_token,
)

from src.core.di.settings import get_settings
from src.domain.identity.models.user import User
from src.domain.identity.models.session import UserSession

from src.domain.identity.services.user import UserService
from src.domain.identity.services.session import SessionService


# ---- settings ---- #
settings = get_settings()
logger = logging.getLogger(__name__)


# ---- Identity Service ---- #
class IdentityService:

    def __init__(self):
        self.user_repo = UserService()
        self.session_repo = SessionService()

    # ------------ register ------------ #
    async def register(self, session: AsyncSession, payload: dict) -> User:

        existing = await self.user_repo.get_by_email(
            session,
            payload["email"],
        )

        if existing:
            raise ValueError("Email already exists")

        user = await self.user_repo.create(
            session,
            {
                "full_name": payload["full_name"],
                "email": payload["email"],
                "user_name": payload["user_name"],
                "password_hash": hash_password(payload["password"]),
            },
        )

        return user

    # ------------ verify email ------------ #
    async def verify_email(self, session: AsyncSession, user_id: str, email: str) -> None:

        user = await self.user_repo.get_by_id(session, UUID(user_id))

        if not user:
            raise ValueError("User not found")

        if user.email != email:
            raise ValueError("Email mismatch")

        if user.is_verified:
            return

        await self.user_repo.update(
            session,
            UUID(user_id),
            {"is_verified": True},
        )

    # ------------ create password reset ------------ #
    async def create_password_reset(self, session: AsyncSession, email: str) -> tuple[str, str]:

        user = await self.user_repo.get_by_email(
            session,
            email,
        )

        if not user:
            raise ValueError("User not found")

        token = create_password_reset_token(
            user_id=str(user.id),
            email=user.email,
        )

        reset_link = (
            f"{settings.app_url}"
            f"/api/v1/identity/reset-password/confirm?token={token}"
        )

        return user.email, reset_link

    # ------------ reset password ------------ #
    async def reset_password(self, session: AsyncSession, token: str, new_password: str):

        payload = decode_password_reset_token(token)

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise ValueError("Invalid token")

        user = await self.user_repo.get_by_id(
            session,
            UUID(user_id),
        )

        if not user or user.email != email:
            raise ValueError("User not found")

        await self.user_repo.update(
            session,
            UUID(user_id),
            {"password_hash": hash_password(new_password)},
        )

        return user

    # ------------ login ------------ #
    async def login(self, session: AsyncSession, payload: dict) -> dict:

        user = await self.user_repo.get_by_email(
            session,
            payload["email"],
        )

        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(payload["password"], user.password_hash):
            raise ValueError("Invalid credentials")

        if not user.is_active:
            raise ValueError("User is inactive")

        user_session = UserSession(
            user_id=user.id,
            ip_address=payload.get("ip_address"),
            user_agent=payload.get("user_agent"),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_expire_days),
        )

        user_session = await self.session_repo.create(session, user_session)

        return self.generate_tokens(user, str(user_session.id))

    # ------------ refresh tokens ------------ #
    async def refresh_tokens(
        self,
        session: AsyncSession,
        user: User,
        session_id: UUID,
    ) -> dict:

        db_session = await self.session_repo.get_by_id(session, session_id)

        if not db_session:
            raise ValueError("Session not found")

        if not db_session.is_active:
            raise ValueError("Session revoked")

        if cast(datetime, db_session.expires_at) < datetime.now(timezone.utc):
            raise ValueError("Session expired")

        return self.generate_tokens(user, str(session_id))

    # ------------ logout ------------ #
    async def logout(self, session: AsyncSession, session_id: UUID) -> None:

        await self.session_repo.update(
            session,
            session_id,
            {"is_active": False},
        )

    # ------------ sessions ------------ #
    async def list_user_sessions(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> list[UserSession]:

        return await self.session_repo.list_by_filters(
            session,
            user_id=user_id,
        )

    async def revoke_all_sessions(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:

        sessions = await self.session_repo.list_by_filters(
            session,
            user_id=user_id,
        )

        for s in sessions:
            s.is_active = False

        await session.commit()

    # ------------ tokens ------------ #
    def generate_tokens(self, user: User, session_id: str) -> dict:

        return {
            "access_token": create_access_token(
                user_id=str(user.id),
                session_id=session_id,
            ),
            "refresh_token": create_refresh_token(
                user_id=str(user.id),
                session_id=session_id,
            ),
        }