from __future__ import annotations

from abc import ABC, abstractmethod

from .models import TranslationRequest, TranslationResult


class BaseTranslator(ABC):
    """Common interface implemented by all translation providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def translate(self, request: TranslationRequest) -> TranslationResult:
        raise NotImplementedError
