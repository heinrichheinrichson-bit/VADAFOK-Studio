"""Optional live test. The API key is read only from the environment."""

import os

from vadafok_studio.translator import (
    DeepLTranslator,
    TranslationRequest,
    TranslatorService,
)

api_key = os.environ.get("DEEPL_API_KEY", "")
service = TranslatorService(DeepLTranslator(api_key=api_key, timeout=5.0))
result = service.translate(
    TranslationRequest(
        text="Hallo Welt",
        source_language="DE",
        target_language="EN",
    )
)

print(f"success: {result.success}")
print(f"provider: {result.provider}")
print(f"time_ms: {result.elapsed_ms:.1f}")
print(f"translation: {result.translated_text}")
print(f"error: {result.error}")
