# ---- imports ---- #
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select

from src.auth.security import security
from src.auth.jwt import decode_token
from src.db.session import session_local
from src.domains.identity.models import User


# ---- protected ---- #
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # ---- decode token ---- #
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ---- extract user id ---- #
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ---- fetch user from DB ---- #
    async with session_local() as session:
        result = await session.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user