# -------------------- imports -------------------- #
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domains.identity.models import User
from src.auth.password import hash_password, verify_password
from src.auth.jwt import create_token


# -------------------- identity service -------------------- #
class UserService:

    # ------------ register ------------ #
    async def register(
        self,
        session: AsyncSession,
        full_name: str,
        email: str,
        password: str,
    ):

        # -------- check existing user -------- #
        result = await session.execute(
            select(User).where(User.email == email)
        )

        existing = result.scalar_one_or_none()

        # -------- validation -------- #
        if existing:
            raise ValueError("Email already exists")

        # -------- create user -------- #
        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
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
        email: str,
        password: str,
    ):

        # -------- fetch user -------- #
        result = await session.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        # -------- authentication -------- #
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        # -------- token generation -------- #
        return create_token({"sub": str(user.id)})