from __future__ import annotations

import json
import logging
import socket
import ssl
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:  # The normal Windows/Python trust store remains the fallback.
    certifi = None

from .base import BaseTranslator
from .exceptions import (
    TranslatorAuthenticationError,
    TranslatorConfigurationError,
    TranslatorProviderError,
    TranslatorQuotaError,
    TranslatorRateLimitError,
    TranslatorTimeoutError,
)
from .models import TranslationRequest, TranslationResult

_LOGGER = logging.getLogger(__name__)

_FREE_ENDPOINT = "https://api-free.deepl.com/v2/translate"
_PRO_ENDPOINT = "https://api.deepl.com/v2/translate"


class DeepLTranslator(BaseTranslator):
    """DeepL REST API provider with no third-party Python dependency."""

    def __init__(
        self,
        api_key: str,
        timeout: float = 2.0,
        use_free_api: bool | None = None,
    ) -> None:
        self._api_key = api_key.strip()
        self._timeout = float(timeout)
        self._use_free_api = (
            self._api_key.endswith(":fx")
            if use_free_api is None
            else bool(use_free_api)
        )

    @property
    def provider_name(self) -> str:
        return "DeepL"

    @property
    def endpoint(self) -> str:
        return _FREE_ENDPOINT if self._use_free_api else _PRO_ENDPOINT

    def translate(self, request: TranslationRequest) -> TranslationResult:
        started = time.perf_counter()

        try:
            self._validate(request)
            payload: dict[str, Any] = {
                "text": [request.text],
                "target_lang": request.target_language,
            }
            if request.source_language:
                payload["source_lang"] = request.source_language

            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            http_request = Request(
                self.endpoint,
                data=body,
                method="POST",
                headers={
                    "Authorization": f"DeepL-Auth-Key {self._api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "VADAFOK-Studio/2.27",
                },
            )

            with urlopen(
                http_request,
                timeout=self._timeout,
                context=self._ssl_context(),
            ) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)

            translation = self._parse_translation(data)
            return TranslationResult(
                success=True,
                translated_text=translation["text"],
                provider=self.provider_name,
                elapsed_ms=self._elapsed_ms(started),
                detected_source_language=str(
                    translation.get("detected_source_language", "")
                ),
            )

        except TranslatorConfigurationError as exc:
            return self._failure(exc, started)
        except HTTPError as exc:
            return self._failure(self._map_http_error(exc), started)
        except (TimeoutError, socket.timeout) as exc:
            return self._failure(
                TranslatorTimeoutError(
                    f"DeepL timed out after {self._timeout:.1f} seconds."
                ),
                started,
            )
        except URLError as exc:
            if isinstance(exc.reason, socket.timeout):
                error = TranslatorTimeoutError(
                    f"DeepL timed out after {self._timeout:.1f} seconds."
                )
            else:
                error = TranslatorProviderError(
                    f"DeepL connection failed: {exc.reason}"
                )
            return self._failure(error, started)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            return self._failure(
                TranslatorProviderError(f"Invalid DeepL response: {exc}"),
                started,
            )
        except Exception as exc:
            _LOGGER.exception("Unexpected DeepL provider failure")
            return self._failure(
                TranslatorProviderError(f"Unexpected DeepL error: {exc}"),
                started,
            )

    @staticmethod
    def _ssl_context() -> ssl.SSLContext:
        """Create a verified TLS context.

        certifi is preferred because embedded/new Python installations can
        otherwise use an incomplete or stale certificate chain. Verification
        is never disabled.
        """

        if certifi is not None:
            return ssl.create_default_context(cafile=certifi.where())
        return ssl.create_default_context()

    def _validate(self, request: TranslationRequest) -> None:
        if not self._api_key:
            raise TranslatorConfigurationError("DeepL API key is missing.")
        if self._timeout <= 0:
            raise TranslatorConfigurationError(
                "DeepL timeout must be greater than zero."
            )
        if not request.text:
            raise TranslatorConfigurationError("Translation text is empty.")
        if not request.target_language:
            raise TranslatorConfigurationError("Target language is missing.")

    @staticmethod
    def _parse_translation(data: Any) -> dict[str, Any]:
        translations = data.get("translations")
        if not isinstance(translations, list) or not translations:
            raise TranslatorProviderError(
                "DeepL response contains no translation."
            )

        translation = translations[0]
        if not isinstance(translation, dict):
            raise TranslatorProviderError(
                "DeepL translation entry has an invalid format."
            )

        text = translation.get("text")
        if not isinstance(text, str) or not text:
            raise TranslatorProviderError(
                "DeepL response contains no translated text."
            )
        return translation

    def _map_http_error(self, error: HTTPError) -> Exception:
        detail = self._read_error_detail(error)

        if error.code in (401, 403):
            return TranslatorAuthenticationError(
                detail or "DeepL rejected the API key."
            )
        if error.code == 429:
            return TranslatorRateLimitError(
                detail or "DeepL rate limit reached."
            )
        if error.code == 456:
            return TranslatorQuotaError(
                detail or "DeepL translation quota exhausted."
            )
        if error.code in (408, 504, 529):
            return TranslatorTimeoutError(
                detail or "DeepL is temporarily unavailable."
            )
        return TranslatorProviderError(
            detail or f"DeepL returned HTTP {error.code}."
        )

    @staticmethod
    def _read_error_detail(error: HTTPError) -> str:
        try:
            raw = error.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            message = data.get("message") or data.get("detail")
            return str(message) if message else raw[:300]
        except Exception:
            return ""

    def _failure(
        self,
        error: Exception,
        started: float,
    ) -> TranslationResult:
        return TranslationResult.failure(
            str(error),
            provider=self.provider_name,
            elapsed_ms=self._elapsed_ms(started),
        )

    @staticmethod
    def _elapsed_ms(started: float) -> float:
        return (time.perf_counter() - started) * 1000.0
