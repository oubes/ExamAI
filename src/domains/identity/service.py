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

        result = await session.execute(
            select(User).where(User.email == payload["email"])
        )

        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError("Email already exists")

        user = User(
            full_name=payload["full_name"],
            email=payload["email"],
            user_name=payload["user_name"],
            password_hash=hash_password(payload["password"]),
        )

        session.add(user)

        await session.commit()
        await session.refresh(user)

        logger.debug(f"[IdentityService] Registered user id={user.id}")

        return user

    # ------------ verify email ------------ #
    async def verify_email(
        self,
        session: AsyncSession,
        user_id: str,
        email: str,
    ) -> None:

        result = await session.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        if user.email != email:
            raise ValueError("Email mismatch")

        if user.is_verified:
            return

        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True)
        )

        await session.commit()

        logger.debug(f"[IdentityService] Verified user id={user_id}")

    # ------------ create password reset ------------ #
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

        reset_link = (
            f"{settings.app_url}"
            f"/api/v1/identity/reset-password/confirm?token={token}"
        )

        logger.debug(f"[IdentityService] Created reset token user_id={user.id}")

        return user.email, reset_link

    # ------------ reset password ------------ #
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

        logger.debug(f"[IdentityService] Reset password user_id={user_id}")

    # ------------ login ------------ #
    async def login(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> dict:

        result = await session.execute(
            select(User).where(User.email == payload["email"])
        )

        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("Invalid credentials")

        # ---- NEW: verification check ---- #
        if not user.is_verified:
            raise ValueError("User is not verified")

        if not verify_password(
            password=payload["password"],
            hashed=user.password_hash,
        ):
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

        session.add(user_session)

        await session.commit()
        await session.refresh(user_session)

        logger.debug(
            f"[IdentityService] Created session id={user_session.id}"
        )

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

        result = await session.execute(
            select(UserSession).where(
                UserSession.id == session_id,
            )
        )

        db_session = result.scalar_one_or_none()

        if not db_session:
            raise ValueError("Session not found")

        if not db_session.is_active:
            raise ValueError("Session revoked")

        if cast(datetime, db_session.expires_at) < datetime.now(timezone.utc):
            raise ValueError("Session expired")

        logger.debug(
            f"[IdentityService] Refreshed tokens session_id={session_id}"
        )

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

        await session.execute(
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(is_active=False)
        )

        await session.commit()

        logger.debug(
            f"[IdentityService] Logged out session_id={session_id}"
        )

    # ------------ get user by id ------------ #
    async def get_user_by_id(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:

        logger.debug(f"[IdentityService] Fetching user id={user_id}")

        return await session.get(User, user_id)

    # ------------ get user by email ------------ #
    async def get_user_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:

        result = await session.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    # ------------ get user by username ------------ #
    async def get_user_by_username(
        self,
        session: AsyncSession,
        user_name: str,
    ) -> User | None:

        result = await session.execute(
            select(User).where(User.user_name == user_name)
        )

        return result.scalar_one_or_none()

    # ------------ list users ------------ #
    async def list_users(
        self,
        session: AsyncSession,
    ) -> list[User]:

        result = await session.execute(select(User))

        rows = result.scalars().all()

        return list(rows)

    # ------------ update user ------------ #
    async def update_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        updates: dict,
    ) -> User:

        user = await session.get(User, user_id)

        if not user:
            raise ValueError("User not found")

        for k, v in updates.items():
            setattr(user, k, v)

        await session.commit()
        await session.refresh(user)

        logger.debug(f"[IdentityService] Updated user id={user_id}")

        return user

    # ------------ delete user ------------ #
    async def delete_user(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:

        user = await session.get(User, user_id)

        if not user:
            raise ValueError("User not found")

        await session.delete(user)

        await session.commit()

        logger.debug(f"[IdentityService] Deleted user id={user_id}")

    # ------------ list user sessions ------------ #
    async def list_user_sessions(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> list[UserSession]:

        result = await session.execute(
            select(UserSession).where(
                UserSession.user_id == user_id
            )
        )

        rows = result.scalars().all()

        return list(rows)

    # ------------ revoke all sessions ------------ #
    async def revoke_all_sessions(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:

        await session.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id)
            .values(is_active=False)
        )

        await session.commit()

        logger.debug(
            f"[IdentityService] Revoked all sessions user_id={user_id}"
        )

    # ------------ exists by email ------------ #
    async def exists_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> bool:

        result = await session.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none() is not None

    # ------------ exists by username ------------ #
    async def exists_by_username(
        self,
        session: AsyncSession,
        user_name: str,
    ) -> bool:

        result = await session.execute(
            select(User).where(User.user_name == user_name)
        )

        return result.scalar_one_or_none() is not None

    # ------------ generate tokens ------------ #
    def generate_tokens(
        self,
        user: User,
        session_id: str,
    ) -> dict:

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