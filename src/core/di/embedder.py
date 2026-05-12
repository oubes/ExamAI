# ---- Imports ---- #
from fastapi import Depends
from src.infra.embedding.service import EmbeddingService
from src.infra.embedding.adapter import EmbeddingClient
from src.core.di.settings import get_settings, Settings

# ---------- Embedding Service ---------- #
async def get_embedding_service(
    settings = get_settings()
):
    return EmbeddingService(EmbeddingClient(settings), settings)