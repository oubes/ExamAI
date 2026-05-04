# ---- imports ---- #
from datetime import datetime, timezone
from typing import ClassVar, Literal
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select

from src.auth.jwt import decode_token
from src.db.session import session_local
from src.domains.identity.models import (
    User,
    UserSession,
)

from src.auth.security import security


# ---------- base auth dependency ---------- #
class BaseAuthDependency:

    token_type: ClassVar[Literal["access", "refresh"]]

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

        # ---- parse ids ---- #
        try:
            user_id = UUID(payload["sub"])
            session_id = UUID(payload["session_id"])

        except Exception:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload",
            )

        # ---- validate session + fetch user ---- #
        async with session_local() as session:

            # ---- fetch session ---- #
            session_result = await session.execute(
                select(UserSession).where(
                    UserSession.id == session_id,
                    UserSession.is_active.is_(True),
                    UserSession.expires_at
                    > datetime.now(timezone.utc),
                )
            )

            user_session = session_result.scalar_one_or_none()

            # ---- validate session ---- #
            if not user_session:
                raise HTTPException(
                    status_code=401,
                    detail="Session expired",
                )

            # ---- fetch user ---- #
            user_result = await session.execute(
                select(User).where(User.id == user_id)
            )

            user = user_result.scalar_one_or_none()

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