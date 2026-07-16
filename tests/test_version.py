from __future__ import annotations
import unittest
from vadafok_studio.version import APP_TITLE, APP_USER_MODEL_ID, PRODUCT_NAME, SIDEBAR_VERSION, VERSION, version_info

class VersionTests(unittest.TestCase):
    def test_current_version(self):
        self.assertEqual(VERSION, "2.24.3")

    def test_values(self):
        self.assertEqual(APP_TITLE, f"{PRODUCT_NAME} {VERSION}")
        self.assertEqual(SIDEBAR_VERSION, f"Studio {VERSION}")
        self.assertEqual(APP_USER_MODEL_ID, f"VADAFOK.Studio.{VERSION}")
        self.assertEqual(version_info()["version"], VERSION)

if __name__ == "__main__":
    unittest.main()
