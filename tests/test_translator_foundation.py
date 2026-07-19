import unittest

from vadafok_studio.translator import (
    BaseTranslator,
    TranslationRequest,
    TranslationResult,
    TranslatorService,
)
from vadafok_studio.translator.deepl import DeepLTranslator


class FakeTranslator(BaseTranslator):
    @property
    def provider_name(self) -> str:
        return "Fake"

    def translate(self, request: TranslationRequest) -> TranslationResult:
        return TranslationResult(
            success=True,
            translated_text=f"{request.text} translated",
            provider=self.provider_name,
        )


class ExplodingTranslator(BaseTranslator):
    @property
    def provider_name(self) -> str:
        return "Exploding"

    def translate(self, request: TranslationRequest) -> TranslationResult:
        raise RuntimeError("boom")


class TranslatorTests(unittest.TestCase):
    def test_service_without_provider_fails_safely(self):
        result = TranslatorService().translate("Hallo", "DE", "EN")
        self.assertFalse(result.success)

    def test_service_accepts_plain_text(self):
        result = TranslatorService(FakeTranslator()).translate(
            " Hallo ", "de", "en"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.translated_text, "Hallo translated")

    def test_provider_exception_never_escapes(self):
        result = TranslatorService(ExplodingTranslator()).translate(
            "Hallo", "DE", "EN"
        )
        self.assertFalse(result.success)
        self.assertIn("boom", result.error)

    def test_deepl_missing_key_fails_without_network(self):
        result = DeepLTranslator("").translate(
            TranslationRequest("Hallo", "DE", "EN")
        )
        self.assertFalse(result.success)
        self.assertIn("key", result.error.lower())

    def test_free_endpoint_auto_detection(self):
        provider = DeepLTranslator("example:fx")
        self.assertIn("api-free.deepl.com", provider.endpoint)


if __name__ == "__main__":
    unittest.main()
