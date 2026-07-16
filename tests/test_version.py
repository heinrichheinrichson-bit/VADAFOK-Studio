from __future__ import annotations
import unittest
from vadafok_studio.version import VERSION

class VersionTests(unittest.TestCase):
    def test_current_version(self):
        self.assertEqual(VERSION, "2.24.5.4")

if __name__ == "__main__":
    unittest.main()
