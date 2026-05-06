# ---- Imports ----
import asyncio
import logging

from src.infra.llm.adapter import LLMClient
from src.core.di.settings import Settings


# ---- Logger ----
logger = logging.getLogger(__name__)


# ---- LLM Service ----
class LLMService:

    # ---- Constructor ----
    def __init__(
        self,
        client: LLMClient,
        settings: Settings,
    ):
        self._client = client.get_client()
        self._model = client.get_model()

        self._config = settings
        self._max_retries = self._config.llm_max_retries
        self._base_delay = self._config.llm_base_delay
        self._max_context_tokens = self._config.llm_max_context_tokens

    # ---- Prompt Safety ----
    def _sanitize_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        sanitized: list[dict[str, str]] = []

        for msg in messages:
            role = (msg.get("role") or "").strip()
            content = (msg.get("content") or "").strip()

            if not role or not content:
                continue

            sanitized.append(
                {
                    "role": role,
                    "content": content[:self._max_context_tokens],
                }
            )

        return sanitized

    # ---- Core Call ----
    async def _call_llm(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    # ---- Public API ----
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 128,
    ) -> str:

        logger.info("LLM generation started")

        safe_messages = self._sanitize_messages(messages)

        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1} | model={self._model}")

                result = await self._call_llm(
                    safe_messages,
                    temperature,
                    max_tokens,
                )

                logger.info("LLM generation succeeded")
                return result

            except Exception as e:
                last_error = e
                error_msg = str(e).lower()

                logger.warning(
                    f"LLM generation failed on attempt {attempt + 1}: {error_msg}"
                )

                if "rate" in error_msg:
                    sleep_time = self._base_delay * (2 ** attempt)
                else:
                    sleep_time = self._base_delay

                await asyncio.sleep(sleep_time)

        logger.error("LLM generation failed after all retries")
        raise last_error if last_error else RuntimeError("Unknown failure")