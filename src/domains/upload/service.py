# ---- imports ---- #
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.upload.models import UploadFileModel


# ---- logging ---- #
logger = logging.getLogger(__name__)


# -------------------- upload repository -------------------- #
class UploadRepository:

    # ---- create upload record ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> UploadFileModel:

        # ---- create record ---- #
        record = UploadFileModel(**data)

        # ---- persist ---- #
        session.add(record)

        await session.commit()
        await session.refresh(record)

        return record