# ---- imports ---- #
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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

            record = UploadFileModel(**data)

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

    # ---- Get record by id ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id,
    ) -> UploadFileModel | None:

        try:
            logger.debug(f"[StorageRepository] Fetching record id={record_id}")

            return await session.get(UploadFileModel, record_id)

        except Exception as e:
            logger.error(
                f"[StorageRepository] Failed to fetch record: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- Delete record ---- #
    async def delete(
        self,
        session: AsyncSession,
        record: UploadFileModel,
    ) -> None:

        try:
            logger.debug(f"[StorageRepository] Deleting record id={record.id}")

            await session.delete(record)
            await session.commit()

        except Exception as e:
            logger.error(
                f"[StorageRepository] Failed to delete record: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- list by user ---- #
    async def list_by_user(
        self,
        session: AsyncSession,
        user_id,
    ) -> list[UploadFileModel]:

        try:
            logger.debug(f"[StorageRepository] Listing uploads user_id={user_id}")

            result = await session.execute(
                select(UploadFileModel).where(
                    UploadFileModel.user_id == user_id
                )
            )

            rows = result.scalars().all()

            return list(rows)

        except Exception as e:
            logger.error(
                f"[StorageRepository] Failed to list uploads: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- update record ---- #
    async def update(
        self,
        session: AsyncSession,
        record_id,
        updates: dict,
    ) -> UploadFileModel:

        try:
            logger.debug(f"[StorageRepository] Updating record id={record_id}")

            record = await session.get(UploadFileModel, record_id)

            if not record:
                raise ValueError("Record not found")

            for k, v in updates.items():
                setattr(record, k, v)

            await session.commit()
            await session.refresh(record)

            logger.debug(f"[StorageRepository] Updated record id={record.id}")

            return record

        except Exception as e:
            logger.error(
                f"[StorageRepository] Failed to update record: {str(e)}",
                exc_info=True,
            )
            raise