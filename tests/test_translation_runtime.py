import os
import unittest
from unittest.mock import patch

from vadafok_studio.translator.models import TranslationResult
from vadafok_studio.translator import runtime


class TranslationRuntimeTests(unittest.TestCase):
    def setUp(self):
        runtime.clear_translation_cache()

    def test_success_is_cached(self):
        fake_service = unittest.mock.Mock()
        fake_service.translate.return_value = TranslationResult(
            success=True,
            translated_text="That was close.",
            provider="DeepL",
        )
        with patch.object(runtime, "_get_service", return_value=fake_service):
            first = runtime.translate_text("Das war knapp.", target_language="EN")
            second = runtime.translate_text("Das war knapp.", target_language="EN")

        self.assertTrue(first.success)
        self.assertEqual(second.translated_text, "That was close.")
        self.assertEqual(fake_service.translate.call_count, 1)

    def test_missing_key_becomes_failure_result(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(runtime, "_service", None):
                result = runtime.translate_text("Hallo", target_language="EN")
        self.assertFalse(result.success)
        self.assertIn("DEEPL_API_KEY", result.error)


if __name__ == "__main__":
    unittest.main()
