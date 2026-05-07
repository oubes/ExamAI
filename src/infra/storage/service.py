# ---- Imports ---- #
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
import aiofiles

from src.core.di.settings import get_settings


# ---- Settings ---- #
settings = get_settings()

# ---- Storage Path ---- #
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---- Storage Service ---- #
class StorageService:

    # ---- Save File ---- #
    async def save_file(
        self,
        file: UploadFile,
        user_id: str,
    ) -> dict:

        if not file.filename:
            raise ValueError("Filename is required")

        # ---- File naming ---- #
        extension = Path(file.filename).suffix
        generated_filename = f"{uuid4().hex}{extension}"

        # ---- Build path (user-based only) ---- #
        file_dir = UPLOAD_DIR / str(user_id)
        file_dir.mkdir(parents=True, exist_ok=True)

        file_path = file_dir / generated_filename

        # ---- Read file ---- #
        content = await file.read()

        # ---- Write async ---- #
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(content)

        # ---- Response ---- #
        return {
            "filename": generated_filename,
            "original_filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "path": str(file_path),
            "relative_path": str(file_path.relative_to(UPLOAD_DIR)),
            "user_id": user_id,
        }