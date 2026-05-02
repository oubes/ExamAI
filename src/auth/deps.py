# ---- imports ---- #
from typing import Literal

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from src.auth.jwt import decode_token
from src.db.session import session_local
from src.domains.identity.models import User


# ---- security ---- #
security = HTTPBearer()


# ---------- base auth dependency ---------- #
class BaseAuthDependency:
    token_type: Literal["access", "refresh"]

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> User:
        # ---- decode token ---- #
        payload = decode_token(credentials.credentials)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized",
            )

        # ---- validate token type ---- #
        if payload.get("type") != self.token_type:
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
            )

        # ---- extract user id ---- #
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        # ---- fetch user ---- #
        async with session_local() as session:
            result = await session.execute(
                select(User).where(User.id == int(user_id))
            )

            user = result.scalar_one_or_none()

        # ---- validate user ---- #
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        return user


# ---------- access auth ---------- #
class AccessAuthDependency(BaseAuthDependency):
    token_type = "access"


# ---------- refresh auth ---------- #
class RefreshAuthDependency(BaseAuthDependency):
    token_type = "refresh"


# ---------- dependency instances ---------- #
get_current_user = AccessAuthDependency()
get_refresh_user = RefreshAuthDependency()