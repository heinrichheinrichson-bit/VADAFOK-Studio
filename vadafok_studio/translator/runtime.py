"""Central translation runtime shared by Quick Cards and Live Card."""

from __future__ import annotations

import logging
import os
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Final

from .deepl import DeepLTranslator
from .models import TranslationResult
from .service import TranslatorService

_CACHE_LIMIT: Final[int] = 128
_DEFAULT_TIMEOUT: Final[float] = 5.0

_lock = threading.RLock()
_service: TranslatorService | None = None
_service_key: str = ""
_cache: "OrderedDict[tuple[str, str, str], TranslationResult]" = OrderedDict()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _logger() -> logging.Logger:
    logger = logging.getLogger("vadafok.translation")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    try:
        log_dir = _project_root() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(
            log_dir / "translation.log",
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
    except OSError:
        logger.addHandler(logging.NullHandler())
    logger.propagate = False
    return logger


def _get_service() -> TranslatorService:
    global _service, _service_key

    api_key = os.environ.get("DEEPL_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DEEPL_API_KEY fehlt.")

    with _lock:
        if _service is None or api_key != _service_key:
            _service = TranslatorService(
                DeepLTranslator(
                    api_key=api_key,
                    timeout=_DEFAULT_TIMEOUT,
                    # A :fx key is automatically routed to DeepL API Free.
                    use_free_api=None,
                )
            )
            _service_key = api_key
        return _service


def translate_text(
    text: str,
    *,
    source_language: str = "",
    target_language: str = "EN",
) -> TranslationResult:
    """Translate text through the shared DeepL service and a small LRU cache."""

    normalized_text = str(text or "").strip()
    source = str(source_language or "").strip().upper()
    target = str(target_language or "EN").strip().upper()
    key = (normalized_text, source, target)

    if not normalized_text:
        return TranslationResult.failure("Translation text is empty.")

    with _lock:
        cached = _cache.get(key)
        if cached is not None:
            _cache.move_to_end(key)
            _logger().info(
                "status=CACHE_HIT source=%s target=%s chars=%d",
                source or "AUTO",
                target,
                len(normalized_text),
            )
            return cached

    try:
        result = _get_service().translate(
            normalized_text,
            source_language=source,
            target_language=target,
        )
    except Exception as exc:
        result = TranslationResult.failure(str(exc), provider="DeepL")

    log = _logger()
    if result.success:
        log.info(
            "status=OK provider=%s source=%s target=%s chars=%d time_ms=%.1f",
            result.provider or "DeepL",
            source or result.detected_source_language or "AUTO",
            target,
            len(normalized_text),
            result.elapsed_ms,
        )
        with _lock:
            _cache[key] = result
            _cache.move_to_end(key)
            while len(_cache) > _CACHE_LIMIT:
                _cache.popitem(last=False)
    else:
        log.warning(
            "status=ERROR provider=%s source=%s target=%s chars=%d error=%s",
            result.provider or "DeepL",
            source or "AUTO",
            target,
            len(normalized_text),
            result.error,
        )

    return result


def clear_translation_cache() -> None:
    with _lock:
        _cache.clear()
