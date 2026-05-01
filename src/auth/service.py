# ---- imports ---- #
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domains.identity.models import User
from src.auth.password import hash_password, verify_password
from src.auth.jwt import create_token


# ---- auth service ---- #
class AuthService:

    # ---- register ---- #
    async def register(
        self,
        session: AsyncSession,
        full_name: str,
        email: str,
        password: str,
    ):
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError("Email already exists")

        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    # ---- login ---- #
    async def login(
        self,
        session: AsyncSession,
        email: str,
        password: str,
    ):
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        return create_token({"sub": str(user.id)})