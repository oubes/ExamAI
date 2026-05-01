# ---- imports ---- #
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.auth.security import security
from src.auth.jwt import decode_token


# ---- protected ---- #
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return payload