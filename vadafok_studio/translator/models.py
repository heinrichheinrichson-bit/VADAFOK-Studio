from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranslationRequest:
    """Input passed to every translation provider."""

    text: str
    source_language: str = ""
    target_language: str = "EN"

    def normalized(self) -> "TranslationRequest":
        return TranslationRequest(
            text=self.text.strip(),
            source_language=self.source_language.strip().upper(),
            target_language=self.target_language.strip().upper(),
        )


@dataclass(frozen=True, slots=True)
class TranslationResult:
    """Provider-independent translation result."""

    success: bool
    translated_text: str = ""
    provider: str = ""
    elapsed_ms: float = 0.0
    error: str = ""
    detected_source_language: str = ""

    @classmethod
    def failure(
        cls,
        error: str,
        *,
        provider: str = "",
        elapsed_ms: float = 0.0,
    ) -> "TranslationResult":
        return cls(
            success=False,
            provider=provider,
            elapsed_ms=elapsed_ms,
            error=error,
        )
