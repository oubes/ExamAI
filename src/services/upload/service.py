# ---- Imports ---- #
from src.infra.storage.service import StorageService
from src.domains.storage.service import StorageRepository
from sqlalchemy.ext.asyncio import AsyncSession

# ---- Services ---- #
storage_service = StorageService()
storage_repository = StorageRepository()


# ---- Upload Service ---- #
class UploadService:

    # ---- Handle Upload ---- #
    async def handle_upload(self, session: AsyncSession, user, file):

        # ---- Save file to disk ---- #
        file_data = await storage_service.save_file(file=file, user_id=user.id)

        # ---- Persist metadata ---- #
        record = await storage_repository.create(
        session=session, 
        data={
            "user_id": user.id,
            "original_name": file_data["original_filename"],
            "stored_name": file_data["filename"],
            "path": file_data["path"],
            "content_type": file_data["content_type"],
            "size": file_data["size"],
        })

        return {
            "file": file_data,
            "record": {
                "id": record.id,
                "stored_name": record.stored_name,
            }
        }