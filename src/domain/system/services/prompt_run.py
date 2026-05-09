"""Prompt run persistence helpers."""

# ---- Imports ---- #
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.system.models.prompt_run import PromptRun


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# -------------------- Prompt Run Service -------------------- #
class PromptRunService:

	# ---- Create ---- #
	async def create(
		self,
		session: AsyncSession,
		*,
		model_name: str,
		prompt: str,
		response: str | None = None,
		token_usage: int = 0,
		latency_ms: float = 0.0,
		confidence: float = 0.0,
	) -> PromptRun:

		try:
			logger.debug("[PromptRunService] Creating prompt run model=%s", model_name)

			record = PromptRun(
				model_name=model_name,
				prompt=prompt,
				response=response,
				token_usage=token_usage,
				latency_ms=latency_ms,
				confidence=confidence,
			)

			session.add(record)

			await session.commit()
			await session.refresh(record)

			return record

		except Exception as e:
			logger.error("[PromptRunService] Failed to create prompt run: %s", str(e), exc_info=True)
			raise
