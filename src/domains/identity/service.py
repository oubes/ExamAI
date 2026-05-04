# -------------------- imports -------------------- #
from datetime import datetime, timedelta, timezone
import logging
from typing import cast
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import (
    create_access_token,
    create_refresh_token,
)
from src.auth.password import (
    hash_password,
    verify_password,
)
from src.core.di.settings import get_settings
from src.domains.identity.models import (
    User,
    UserSession,
)


# -------------------- settings -------------------- #
settings = get_settings()

# ---- logging ---- #
logger = logging.getLogger(__name__)


# -------------------- identity service -------------------- #
class IdentityService:

    # ------------ register ------------ #
    async def register(self, session: AsyncSession, payload: dict) -> User:

        # -------- check existing user -------- #
        result = await session.execute(
            select(User).where(User.email == payload["email"])
        )

        existing = result.scalar_one_or_none()

        # -------- validation -------- #
        if existing:
            logger.warning(
                "Register failed: email already exists | email=%s",
                payload["email"],
            )
            raise ValueError("Email already exists")

        # -------- create user -------- #
        user = User(
            full_name=payload["full_name"],
            email=payload["email"],
            user_name=payload["user_name"],
            password_hash=hash_password(payload["password"]),
        )

        # -------- persist -------- #
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user

    # ------------ login ------------ #
    async def login(self, session: AsyncSession, payload: dict) -> dict:

        # -------- fetch user -------- #
        result = await session.execute(
            select(User).where(User.email == payload["email"])
        )

        user = result.scalar_one_or_none()

        # -------- authentication -------- #
        if not user:
            logger.warning(
                "Login failed: user not found | email=%s",
                payload["email"],
            )
            raise ValueError("Invalid credentials")

        if not verify_password(
            password=payload["password"],
            hashed=user.password_hash,
        ):
            logger.warning(
                "Login failed: invalid password | user_id=%s email=%s",
                user.id,
                user.email,
            )
            raise ValueError("Invalid credentials")

        # -------- create session -------- #
        user_session = UserSession(
            user_id=user.id,
            ip_address=payload.get("ip_address"),
            user_agent=payload.get("user_agent"),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_expire_days),
        )

        session.add(user_session)

        await session.commit()
        await session.refresh(user_session)

        return self.generate_tokens(
            user=user,
            session_id=str(user_session.id),
        )

    # ------------ refresh tokens ------------ #
    async def refresh_tokens(
        self,
        session: AsyncSession,
        user: User,
        session_id: UUID,
    ) -> dict:

        # -------- fetch session -------- #
        result = await session.execute(
            select(UserSession).where(UserSession.id == session_id)
        )

        db_session = result.scalar_one_or_none()

        # -------- validate session -------- #
        if not db_session:
            logger.warning("Refresh failed: session not found | session_id=%s", session_id)
            raise ValueError("Session not found")

        if not db_session.is_active:
            logger.warning("Refresh failed: session revoked | session_id=%s", session_id)
            raise ValueError("Session revoked")

        if cast(datetime, db_session.expires_at) < datetime.now(timezone.utc):
            logger.warning("Refresh failed: session expired | session_id=%s", session_id)
            raise ValueError("Session expired")

        # -------- rotate tokens -------- #
        return self.generate_tokens(
            user=user,
            session_id=str(session_id),
        )

    # ------------ logout ------------ #
    async def logout(self, session: AsyncSession, session_id: UUID) -> None:

        result = await session.execute(
            select(UserSession.id).where(UserSession.id == session_id)
        )

        if not result.scalar_one_or_none():
            logger.warning("Logout called for missing session | session_id=%s", session_id)

        await session.execute(
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(is_active=False)
        )

        await session.commit()

    # ------------ generate tokens ------------ #
    def generate_tokens(self, user: User, session_id: str) -> dict:

        access_token = create_access_token(
            user_id=str(user.id),
            session_id=session_id,
        )

        refresh_token = create_refresh_token(
            user_id=str(user.id),
            session_id=session_id,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }