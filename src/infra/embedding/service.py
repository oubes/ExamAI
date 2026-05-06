# ---- Imports ----
import logging
import asyncio

from openai import AsyncOpenAI
from src.core.config.settings import Settings
from src.infra.embedding.adapter import EmbeddingClient

# ---- Logger Initialization ----
logger = logging.getLogger(__name__)


# ---- Embedding Service ----
class EmbeddingService:

    # ---- Constructor ----
    def __init__(
        self,
        client: EmbeddingClient,
        settings: Settings,
    ):
        logger.debug("Initializing EmbeddingService")

        self._client: AsyncOpenAI = client.get_client()
        self._model = client.get_model()
        
        self.max_concurrency = settings.alibaba_embeddings_max_concurrency
        self._max_retries = settings.alibaba_embeddings_max_retries
        self._base_delay = settings.alibaba_embeddings_base_delay

        self._semaphore = asyncio.Semaphore(self.max_concurrency)

        logger.debug("EmbeddingService initialized using model: %s", self._model)

    # ---- Prompt Safety ----
    def _sanitize_texts(self, texts: list[str]) -> list[str]:
        sanitized: list[str] = []

        for text in texts:
            clean = (text or "").strip()
            if not clean:
                continue

            sanitized.append(clean[:4000])

        return sanitized

    # ---- Core Call ----
    async def _call_embedding(self, input_data: list[str] | str):
        return await self._client.embeddings.create(
            model=self._model,
            input=input_data,
        )

    # ---- Single ----
    async def embed(self, text: str) -> list[float]:
        safe_texts = self._sanitize_texts([text])
        if not safe_texts:
            return []

        async with self._semaphore:
            last_error: Exception | None = None

            for attempt in range(self._max_retries):
                try:
                    logger.debug(f"Embedding attempt {attempt + 1}")

                    response = await self._call_embedding(safe_texts[0])

                    logger.debug("Single embedding succeeded")
                    return response.data[0].embedding

                except Exception as e:
                    last_error = e
                    error_msg = str(e).lower()

                    logger.warning(
                        f"Embedding failed attempt {attempt + 1}: {error_msg}"
                    )

                    sleep_time = (
                        self._base_delay * (2 ** attempt)
                        if "rate" in error_msg
                        else self._base_delay
                    )

                    await asyncio.sleep(sleep_time)

            logger.error("Single embedding failed after retries")
            raise last_error if last_error else RuntimeError("Unknown failure")

    # ---- Batch Worker ----
    async def _embed_batch_worker(self, batch: list[str]) -> list[list[float]]:
        safe_batch = self._sanitize_texts(batch)

        async with self._semaphore:
            last_error: Exception | None = None

            for attempt in range(self._max_retries):
                try:
                    logger.debug(f"Batch attempt {attempt + 1} | size={len(safe_batch)}")

                    response = await self._call_embedding(safe_batch)

                    logger.debug("Batch embedding succeeded")
                    return [item.embedding for item in response.data]

                except Exception as e:
                    last_error = e
                    error_msg = str(e).lower()

                    logger.warning(
                        f"Batch embedding failed attempt {attempt + 1}: {error_msg}"
                    )

                    sleep_time = (
                        self._base_delay * (2 ** attempt)
                        if "rate" in error_msg
                        else self._base_delay
                    )

                    await asyncio.sleep(sleep_time)

            logger.error("Batch worker failed after retries")
            raise last_error if last_error else RuntimeError("Unknown failure")

    # ---- Batch ----
    async def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 10
    ) -> list[list[float]]:

        logger.debug("Batch embedding started | total=%d", len(texts))

        sanitized = self._sanitize_texts(texts)

        batches: list[list[str]] = [
            sanitized[i:i + batch_size]
            for i in range(0, len(sanitized), batch_size)
        ]

        tasks = [self._embed_batch_worker(batch) for batch in batches]

        results = await asyncio.gather(*tasks)

        embeddings: list[list[float]] = []
        for batch in results:
            embeddings.extend(batch)

        logger.debug("Batch embedding completed | batches=%d", len(batches))
        return embeddings