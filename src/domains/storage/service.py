# ---- imports ---- #
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.storage.models import UploadFileModel


# ---- logging ---- #
logger = logging.getLogger(__name__)


# -------------------- storage repository -------------------- #
class StorageRepository:

    # ---- create storage record ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> UploadFileModel:

        try:
            logger.debug(f"[StorageRepository] Creating upload record: {data}")

            # ---- create record ---- #
            record = UploadFileModel(**data)

            # ---- persist ---- #
            session.add(record)
            await session.commit()
            await session.refresh(record)

            logger.debug(f"[StorageRepository] Created record id={record.id}")

            return record

        except Exception as e:
            logger.error(
                f"[StorageRepository] Failed to create upload record: {str(e)}",
                exc_info=True,
            )
            raise