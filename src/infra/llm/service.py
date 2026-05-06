# ---- Imports ---- #
import asyncio
import logging

from src.infra.llm.adapter import LLMClient
from src.core.di.settings import Settings


# ---- Logger ---- #
logger = logging.getLogger(__name__)


# ---- LLM Service ---- #
class LLMService:

    # ---- Constructor ---- #
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

        self._semaphore = asyncio.Semaphore(
            self._config.llm_max_concurrent_requests
        )

        logger.debug(f"LLMService initialized | model={self._model}")

    # ---- Prompt Safety ---- #
    def _sanitize_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        logger.debug(f"Sanitizing messages | input_count={len(messages)}")

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

        logger.debug(f"Sanitized messages | output_count={len(sanitized)}")
        return sanitized

    # ---- Core Call ---- #
    async def _call_llm(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:

        logger.debug(
            f"Calling LLM | model={self._model} | messages={len(messages)} | temp={temperature} | max_tokens={max_tokens}"
        )

        async with self._semaphore:
            logger.debug("Semaphore acquired")

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )

        logger.debug("Semaphore released")

        content = response.choices[0].message.content or ""

        logger.debug(f"LLM response received | length={len(content)}")
        return content

    # ---- Public API ---- #
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
                logger.debug(
                    f"Generate attempt={attempt + 1} | model={self._model} | messages={len(safe_messages)}"
                )

                result = await self._call_llm(
                    safe_messages,
                    temperature,
                    max_tokens,
                )

                logger.info("LLM generation succeeded")
                logger.debug(f"Generation output length={len(result)}")

                return result

            except Exception as e:
                last_error = e
                error_msg = str(e).lower()

                logger.warning(
                    f"LLM generation failed attempt={attempt + 1} | error={error_msg}"
                )

                if "rate" in error_msg:
                    sleep_time = self._base_delay * (2 ** attempt)
                else:
                    sleep_time = self._base_delay

                logger.debug(f"Retry sleep {sleep_time}s")
                await asyncio.sleep(sleep_time)

        logger.error("LLM generation failed after all retries")
        raise last_error if last_error else RuntimeError("Unknown failure")

    # ---- CrewAI Compatible Interface ---- #
    class Crew:

        # ---- Constructor ---- #
        def __init__(self, outer: "LLMService"):
            self._outer = outer
            logger.debug("CrewAI interface initialized")

        # ---- Chat Namespace ---- #
        class chat:

            # ---- Completions Namespace ---- #
            class completions:

                # ---- Constructor ---- #
                def __init__(self, outer: "LLMService"):
                    self._outer = outer

                # ---- Create ---- #
                async def create(
                    self,
                    model: str,
                    messages: list[dict[str, str]],
                    temperature: float = 0.0,
                    max_tokens: int = 128,
                    **kwargs,
                ):

                    logger.debug(
                        f"CrewAI create called | model={model} | messages={len(messages)}"
                    )

                    return await self._outer._crew_generate(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )

    # ---- CrewAI Execution Path ---- #
    async def _crew_generate(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ):

        logger.info("CrewAI generation started")

        safe_messages = self._sanitize_messages(messages)

        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                logger.debug(
                    f"CrewAI attempt={attempt + 1} | model={model} | messages={len(safe_messages)}"
                )

                result = await self._call_llm(
                    safe_messages,
                    temperature,
                    max_tokens,
                )

                logger.info("CrewAI generation succeeded")
                logger.debug(f"CrewAI output length={len(result)}")

                return type(
                    "Response",
                    (),
                    {
                        "choices": [
                            type(
                                "Choice",
                                (),
                                {
                                    "message": type(
                                        "Message",
                                        (),
                                        {"content": result},
                                    )(),
                                },
                            )(),
                        ],
                    },
                )()

            except Exception as e:
                last_error = e
                error_msg = str(e).lower()

                logger.warning(
                    f"CrewAI generation failed attempt={attempt + 1} | error={error_msg}"
                )

                if "rate" in error_msg:
                    sleep_time = self._base_delay * (2 ** attempt)
                else:
                    sleep_time = self._base_delay

                logger.debug(f"CrewAI retry sleep {sleep_time}s")
                await asyncio.sleep(sleep_time)

        logger.error("CrewAI generation failed after all retries")
        raise last_error if last_error else RuntimeError("Unknown failure")

    # ---- CrewAI Factory ---- #
    def crew(self):
        logger.debug("CrewAI factory called")
        return self.__class__.Crew(self)