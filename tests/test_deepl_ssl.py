import ssl
import unittest
from unittest.mock import patch

from vadafok_studio.translator.deepl import DeepLTranslator


class DeepLSslTests(unittest.TestCase):
    def test_ssl_verification_is_enabled(self):
        context = DeepLTranslator._ssl_context()
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)


if __name__ == "__main__":
    unittest.main()
