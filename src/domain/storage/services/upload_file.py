# ---- Imports ---- #
import logging
import uuid

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from src.domains.storage.models import UploadFileModel


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Upload Service ---- #
class UploadService:

    # ---- Create Upload ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> UploadFileModel:

        try:
            logger.debug(f"[UploadService] create: {data}")

            # ---- check duplicate stored_name ---- #
            stmt = select(UploadFileModel).where(
                UploadFileModel.stored_name == data.get("stored_name")
            )
            result = await session.execute(stmt)

            if result.scalar_one_or_none():
                raise ValueError("stored_name already exists")

            record = UploadFileModel(**data)

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[UploadService] create error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        file_id: uuid.UUID,
    ) -> UploadFileModel | None:

        try:
            return await session.get(UploadFileModel, file_id)

        except Exception as e:
            logger.error(f"[UploadService] get_by_id error: {e}", exc_info=True)
            raise


    # ---- Get By User ---- #
    async def get_by_user(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[UploadFileModel]:

        try:
            stmt = select(UploadFileModel).where(
                UploadFileModel.user_id == user_id
            )

            if category:
                stmt = stmt.where(UploadFileModel.category == category)

            stmt = stmt.order_by(UploadFileModel.created_at.desc())
            stmt = stmt.offset(offset).limit(limit)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[UploadService] get_by_user error: {e}", exc_info=True)
            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        query: str,
    ) -> list[UploadFileModel]:

        try:
            stmt = select(UploadFileModel).where(
                and_(
                    UploadFileModel.user_id == user_id,
                    or_(
                        UploadFileModel.original_name.ilike(f"%{query}%"),
                        UploadFileModel.stored_name.ilike(f"%{query}%"),
                        UploadFileModel.path.ilike(f"%{query}%"),
                    ),
                )
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[UploadService] search error: {e}", exc_info=True)
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        file_id: uuid.UUID,
        updates: dict,
    ) -> UploadFileModel:

        try:
            record = await session.get(UploadFileModel, file_id)

            if not record:
                raise ValueError("upload not found")

            # ---- protected fields ---- #
            protected = {"id", "user_id", "created_at"}

            for k, v in updates.items():
                if k in protected:
                    continue
                setattr(record, k, v)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[UploadService] update error: {e}", exc_info=True)
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        file_id: uuid.UUID,
    ) -> bool:

        try:
            record = await session.get(UploadFileModel, file_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            logger.error(f"[UploadService] delete error: {e}", exc_info=True)
            raise


    # ---- Delete By User ---- #
    async def delete_by_user(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> int:

        try:
            stmt = select(UploadFileModel).where(
                UploadFileModel.user_id == user_id
            )

            result = await session.execute(stmt)
            records = result.scalars().all()

            count = len(records)

            for r in records:
                await session.delete(r)

            await session.commit()

            return count

        except Exception as e:
            logger.error(f"[UploadService] delete_by_user error: {e}", exc_info=True)
            raise


    # ---- Bulk Delete ---- #
    async def bulk_delete(
        self,
        session: AsyncSession,
        ids: list[uuid.UUID],
    ) -> int:

        try:
            stmt = select(UploadFileModel).where(
                UploadFileModel.id.in_(ids)
            )

            result = await session.execute(stmt)
            records = result.scalars().all()

            count = len(records)

            for r in records:
                await session.delete(r)

            await session.commit()

            return count

        except Exception as e:
            logger.error(f"[UploadService] bulk_delete error: {e}", exc_info=True)
            raise


    # ---- Mark Processing ---- #
    async def mark_processing(
        self,
        session: AsyncSession,
        file_id: uuid.UUID,
    ) -> UploadFileModel:

        record = await session.get(UploadFileModel, file_id)

        if not record:
            raise ValueError("upload not found")

        record.processing_status = "processing"

        await session.commit()
        await session.refresh(record)

        return record


    # ---- Mark Processed ---- #
    async def mark_processed(
        self,
        session: AsyncSession,
        file_id: uuid.UUID,
    ) -> UploadFileModel:

        record = await session.get(UploadFileModel, file_id)

        if not record:
            raise ValueError("upload not found")

        record.is_processed = True
        record.processing_status = "completed"
        record.processing_error = None

        await session.commit()
        await session.refresh(record)

        return record


    # ---- Mark Failed ---- #
    async def mark_failed(
        self,
        session: AsyncSession,
        file_id: uuid.UUID,
        error: str,
    ) -> UploadFileModel:

        record = await session.get(UploadFileModel, file_id)

        if not record:
            raise ValueError("upload not found")

        record.is_processed = False
        record.processing_status = "failed"
        record.processing_error = error

        await session.commit()
        await session.refresh(record)

        return record


    # ---- Retry Failed ---- #
    async def retry_failed(
        self,
        session: AsyncSession,
        file_id: uuid.UUID,
    ) -> UploadFileModel:

        record = await session.get(UploadFileModel, file_id)

        if not record:
            raise ValueError("upload not found")

        if record.processing_status != "failed":
            raise ValueError("upload is not in failed state")

        record.processing_status = "pending"
        record.processing_error = None

        await session.commit()
        await session.refresh(record)

        return record


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> dict:

        total = await session.execute(
            select(func.count()).where(
                UploadFileModel.user_id == user_id
            )
        )

        processed = await session.execute(
            select(func.count()).where(
                and_(
                    UploadFileModel.user_id == user_id,
                    UploadFileModel.is_processed == True,
                )
            )
        )

        failed = await session.execute(
            select(func.count()).where(
                and_(
                    UploadFileModel.user_id == user_id,
                    UploadFileModel.processing_status == "failed",
                )
            )
        )

        return {
            "total": total.scalar(),
            "processed": processed.scalar(),
            "failed": failed.scalar(),
        }