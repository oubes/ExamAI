# ---- imports ---- #
from collections.abc import Sequence

from fastapi import Depends, HTTPException

from src.domain.identity.models.user import User

from .auth import get_current_user


# ---------- role checker ---------- #
class RoleChecker:

    def __init__(
        self,
        allowed_roles: Sequence[str],
    ) -> None:

        self.allowed_roles = allowed_roles

    def __call__(
        self,
        user: User = Depends(get_current_user),
    ) -> User:

        # ---- validate role ---- #
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )

        return user


# ---------- role dependencies ---------- #
admin_required = RoleChecker(
    allowed_roles=["admin"],
)

user_required = RoleChecker(
    allowed_roles=["user", "admin"],
)