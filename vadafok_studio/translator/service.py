from __future__ import annotations

import logging
from typing import Optional

from .base import BaseTranslator
from .models import TranslationRequest, TranslationResult

_LOGGER = logging.getLogger(__name__)


class TranslatorService:
    """Safe application-facing entry point for text translation."""

    def __init__(self, provider: Optional[BaseTranslator] = None) -> None:
        self._provider = provider

    @property
    def provider(self) -> Optional[BaseTranslator]:
        return self._provider

    def register(self, provider: BaseTranslator) -> None:
        self._provider = provider

    def clear(self) -> None:
        self._provider = None

    def available(self) -> bool:
        return self._provider is not None

    def translate(
        self,
        request_or_text: TranslationRequest | str,
        source_language: str = "",
        target_language: str = "EN",
    ) -> TranslationResult:
        request = (
            request_or_text
            if isinstance(request_or_text, TranslationRequest)
            else TranslationRequest(
                text=request_or_text,
                source_language=source_language,
                target_language=target_language,
            )
        ).normalized()

        if not request.text:
            return TranslationResult.failure("Translation text is empty.")

        if not request.target_language:
            return TranslationResult.failure("Target language is missing.")

        if self._provider is None:
            return TranslationResult.failure(
                "No translation provider is registered."
            )

        try:
            result = self._provider.translate(request)
        except Exception as exc:
            # Translation must never break the existing Quick Card workflow.
            _LOGGER.exception(
                "TRANSLATOR provider=%s status=UNHANDLED_ERROR",
                self._provider.provider_name,
            )
            return TranslationResult.failure(
                f"Unexpected translator error: {exc}",
                provider=self._provider.provider_name,
            )

        if result.success:
            _LOGGER.info(
                "TRANSLATOR provider=%s source=%s target=%s time_ms=%.1f status=OK",
                result.provider,
                request.source_language or result.detected_source_language or "AUTO",
                request.target_language,
                result.elapsed_ms,
            )
        else:
            _LOGGER.warning(
                "TRANSLATOR provider=%s source=%s target=%s time_ms=%.1f "
                "status=ERROR error=%s",
                result.provider or self._provider.provider_name,
                request.source_language or "AUTO",
                request.target_language,
                result.elapsed_ms,
                result.error,
            )
        return result
