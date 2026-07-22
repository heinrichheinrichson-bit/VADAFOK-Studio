import unittest

from vadafok_studio.version import (
    APP_TITLE,
    APP_USER_MODEL_ID,
    PRODUCT_NAME,
    SIDEBAR_VERSION,
    VERSION,
    version_info,
)


class VersionTests(unittest.TestCase):
    def test_current_version(self):
        assert VERSION == "2.29.0.17"


    def test_runtime_version_constants_are_available(self):
        assert PRODUCT_NAME == "VADAFOK Studio"
        assert APP_TITLE == "VADAFOK Studio 2.29.0.17"
        assert SIDEBAR_VERSION == "Studio 2.29.0.17"
        assert APP_USER_MODEL_ID == "VADAFOK.Studio.2.29.0.17"


    def test_version_info_contains_runtime_values(self):
        assert version_info() == {
            "product_name": PRODUCT_NAME,
            "version": VERSION,
            "app_title": APP_TITLE,
            "sidebar_version": SIDEBAR_VERSION,
            "app_user_model_id": APP_USER_MODEL_ID,
        }
