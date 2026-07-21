from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.obs_workflow.controller import OBSWorkflowController


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
PAGE_PATH = ROOT / "vadafok_studio" / "obs_workflow" / "page.py"


class OBSWorkflowPageTests(unittest.TestCase):
    def test_app_routes_page_through_controller(self):
        app_source = APP_PATH.read_text(encoding="utf-8")
        page_source = PAGE_PATH.read_text(encoding="utf-8")

        self.assertIn("return self.obs_workflow_controller.show_obs_workflow_page()", app_source)
        self.assertNotIn('page_title("OBS Workflow Dashboard")', app_source)
        self.assertIn('page_title("OBS Workflow Dashboard")', page_source)

    def test_app_page_method_is_a_thin_adapter(self):
        tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "show_obs_workflow_page"
        )
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)

    @patch("vadafok_studio.obs_workflow.controller.show_obs_workflow_page")
    def test_controller_delegates_to_page_builder(self, page_builder):
        app = SimpleNamespace()
        page_builder.return_value = Mock()

        result = OBSWorkflowController(app).show_obs_workflow_page()

        page_builder.assert_called_once_with(app)
        self.assertIs(result, page_builder.return_value)


if __name__ == "__main__":
    unittest.main()
