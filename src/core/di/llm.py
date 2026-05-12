# ---- Imports ---- #
from fastapi import Depends
from src.infra.embedding.adapter import EmbeddingClient
from src.infra.embedding.service import EmbeddingService
from src.infra.llm.service import LLMService
from src.infra.llm.adapter import LLMClient
from src.core.di.settings import get_settings, Settings

# ---------- LLM Service ---------- #
async def get_llm_service(
    settings = get_settings()
):
    return LLMService(LLMClient(settings), settings)