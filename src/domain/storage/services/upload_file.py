# ---- Imports ---- #
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from src.domain.storage.models.upload_file import UploadFile


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Upload Service ---- #
class UploadService:

    # ---- Create Upload ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> UploadFile:

        try:
            logger.debug(f"[UploadService] create: {data}")

            # ---- check duplicate stored_name ---- #
            stmt = select(UploadFile).where(
                UploadFile.stored_name == data.get("stored_name")
            )
            result = await session.execute(stmt)

            if result.scalar_one_or_none():
                raise ValueError("stored_name already exists")

            record = UploadFile(**data)

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
    ) -> UploadFile | None:

        try:
            return await session.get(UploadFile, file_id)

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
    ) -> list[UploadFile]:

        try:
            stmt = select(UploadFile).where(
                UploadFile.user_id == user_id
            )

            if category:
                stmt = stmt.where(UploadFile.category == category)

            stmt = stmt.order_by(UploadFile.created_at.desc())
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
    ) -> list[UploadFile]:

        try:
            stmt = select(UploadFile).where(
                and_(
                    UploadFile.user_id == user_id,
                    or_(
                        UploadFile.original_name.ilike(f"%{query}%"),
                        UploadFile.stored_name.ilike(f"%{query}%"),
                        UploadFile.path.ilike(f"%{query}%"),
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
    ) -> UploadFile:

        try:
            record = await session.get(UploadFile, file_id)

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
            record = await session.get(UploadFile, file_id)

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
            stmt = select(UploadFile).where(
                UploadFile.user_id == user_id
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
            stmt = select(UploadFile).where(
                UploadFile.id.in_(ids)
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
    ) -> UploadFile:

        record = await session.get(UploadFile, file_id)

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
    ) -> UploadFile:

        record = await session.get(UploadFile, file_id)

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
    ) -> UploadFile:

        record = await session.get(UploadFile, file_id)

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
    ) -> UploadFile:

        record = await session.get(UploadFile, file_id)

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
                UploadFile.user_id == user_id
            )
        )

        processed = await session.execute(
            select(func.count()).where(
                and_(
                    UploadFile.user_id == user_id,
                    UploadFile.is_processed == True,
                )
            )
        )

        failed = await session.execute(
            select(func.count()).where(
                and_(
                    UploadFile.user_id == user_id,
                    UploadFile.processing_status == "failed",
                )
            )
        )

        return {
            "total": total.scalar(),
            "processed": processed.scalar(),
            "failed": failed.scalar(),
        }