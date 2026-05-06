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
from src.auth.email_token import (
    create_password_reset_token,
    decode_password_reset_token,
)


# -------------------- settings -------------------- #
settings = get_settings()

# ---- logging ---- #
logger = logging.getLogger(__name__)

# -------------------- identity service -------------------- #
class IdentityService:

    # ------------ register ------------ #
    async def register(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> User:

        # -------- check existing user -------- #
        result = await session.execute(
            select(User).where(User.email == payload["email"])
        )

        existing = result.scalar_one_or_none()

        # -------- validation -------- #
        if existing:
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

    # ------------ verify email ------------ #
    async def verify_email(
        self,
        session: AsyncSession,
        user_id: str,
        email: str,
    ) -> None:

        # -------- fetch user -------- #
        result = await session.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        # -------- validations -------- #
        if not user:
            raise ValueError("User not found")

        if user.email != email:
            raise ValueError("Email mismatch")

        if user.is_verified:
            return

        # -------- update user -------- #
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True)
        )

        await session.commit()
        
# -------------------- reset password -------------------- #

    # ---- request reset ---- #
    async def create_password_reset(
        self,
        session: AsyncSession,
        email: str,
    ) -> tuple[str, str]:

        result = await session.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        token = create_password_reset_token(
            user_id=str(user.id),
            email=user.email,
        )

        reset_link = f"{settings.app_url}/api/v1/identity/reset-password/confirm?token={token}"

        return user.email, reset_link


    # ---- confirm reset ---- #
    async def reset_password(
        self,
        session: AsyncSession,
        token: str,
        new_password: str,
    ) -> None:

        payload = decode_password_reset_token(token)

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise ValueError("Invalid token")

        result = await session.execute(
            select(User).where(
                User.id == user_id,
                User.email == email,
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=hash_password(new_password))
        )

        await session.commit()
    # ------------ login ------------ #
    async def login(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> dict:

        # -------- fetch user -------- #
        result = await session.execute(
            select(User).where(User.email == payload["email"])
        )

        user = result.scalar_one_or_none()

        # -------- authentication -------- #
        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(
            password=payload["password"],
            hashed=user.password_hash,
        ):
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

        # -------- generate tokens -------- #
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
            select(UserSession).where(
                UserSession.id == session_id,
            )
        )

        db_session = result.scalar_one_or_none()

        # -------- validate session -------- #
        if not db_session:
            raise ValueError("Session not found")

        if not db_session.is_active:
            raise ValueError("Session revoked")

        if cast(datetime, db_session.expires_at) < datetime.now(timezone.utc):
            raise ValueError("Session expired")

        # -------- rotate tokens -------- #
        return self.generate_tokens(
            user=user,
            session_id=str(session_id),
        )

    # ------------ logout ------------ #
    async def logout(
        self,
        session: AsyncSession,
        session_id: UUID,
    ) -> None:

        # -------- deactivate session -------- #
        await session.execute(
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(is_active=False)
        )

        await session.commit()

    # ------------ generate tokens ------------ #
    def generate_tokens(
        self,
        user: User,
        session_id: str,
    ) -> dict:

        # -------- create access token -------- #
        access_token = create_access_token(
            user_id=str(user.id),
            session_id=session_id,
        )

        # -------- create refresh token -------- #
        refresh_token = create_refresh_token(
            user_id=str(user.id),
            session_id=session_id,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }