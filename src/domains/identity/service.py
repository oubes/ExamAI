# -------------------- imports -------------------- #
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
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


# -------------------- identity service -------------------- #
class IdentityService:

    # ------------ register ------------ #
    async def register(
        self,
        session: AsyncSession,
        payload: dict,
    ):

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

    # ------------ login ------------ #
    async def login(
        self,
        session: AsyncSession,
        payload: dict,
    ):

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
            ip_address=payload["ip_address"],
            user_agent=payload["user_agent"],
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

    # ------------ generate tokens ------------ #
    def generate_tokens(
        self,
        user: User,
        session_id: str,
    ):

        # -------- create jwt tokens -------- #
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