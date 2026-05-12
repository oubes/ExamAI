# ---- Imports ---- #
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.storage.service import StorageService
from src.domain.storage.services.upload_file import (
    UploadService as UploadCrudService
)


# ---- Services ---- #
storage_service = StorageService()
upload_crud = UploadCrudService()


# ---- Upload Service ---- #
class UploadService:

    # ---- Handle Upload ---- #
    async def handle_upload(
        self,
        session: AsyncSession,
        user,
        category,
        file,
    ):
        # ---- Save File (Disk) ---- #
        file_data = await storage_service.save_file(
            file=file,
            user_id=user.id,
        )

        # ---- Persist Metadata (DB) ---- #
        record = await upload_crud.create(
            session=session,
            data={
                "user_id": user.id,
                "original_name": file_data["original_filename"],
                "stored_name": file_data["filename"],
                "path": file_data["path"],
                "content_type": file_data["content_type"],
                "size": file_data["size"],
                "category": category,
            },
        )

        # ---- FIX: return full ORM object for response_model ---- #
        return record

    # ---- Get Upload ---- #
    async def get_upload(
        self,
        session: AsyncSession,
        file_id,
    ):
        return await upload_crud.get_by_id(
            session=session,
            file_id=file_id,
        )

    # ---- Get User Uploads ---- #
    async def get_user_uploads(
        self,
        session: AsyncSession,
        user_id,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        return await upload_crud.get_by_user(
            session=session,
            user_id=user_id,
            category=category,
            limit=limit,
            offset=offset,
        )

    # ---- Delete Upload (DB + File) ---- #
    async def delete_upload(
        self,
        session: AsyncSession,
        file_id,
    ):
        # ---- Fetch Record ---- #
        record = await upload_crud.get_by_id(
            session=session,
            file_id=file_id,
        )

        if not record:
            return False

        file_path = Path(record.path)

        # ---- Delete DB ---- #
        deleted = await upload_crud.delete(
            session=session,
            file_id=file_id,
        )

        # ---- Delete File ---- #
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            # file system failure should NOT break API
            pass

        return deleted

    # ---- Delete By User (DB + Files) ---- #
    async def delete_user_uploads(
        self,
        session: AsyncSession,
        user_id,
    ):
        records = await upload_crud.get_by_user(
            session=session,
            user_id=user_id,
            limit=10_000,
            offset=0,
        )

        count = 0

        for record in records:

            file_path = Path(record.path)

            await upload_crud.delete(
                session=session,
                file_id=record.id,
            )

            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass

            count += 1

        return count

    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        user_id,
    ):
        return await upload_crud.stats(
            session=session,
            user_id=user_id,
        )