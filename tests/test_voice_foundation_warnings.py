from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FOUNDATION_FILE = PROJECT_ROOT / "vadafok_studio" / "voice_control" / "foundation.py"


class VoiceFoundationWarningTests(unittest.TestCase):
    def test_no_return_inside_finally_block(self) -> None:
        tree = ast.parse(
            FOUNDATION_FILE.read_text(encoding="utf-8"),
            filename=str(FOUNDATION_FILE),
        )
        violations = []

        class Visitor(ast.NodeVisitor):
            def visit_Try(self, node: ast.Try) -> None:
                for statement in node.finalbody:
                    for child in ast.walk(statement):
                        if isinstance(child, ast.Return):
                            violations.append(child.lineno)
                self.generic_visit(node)

        Visitor().visit(tree)
        self.assertEqual(violations, [])

    def test_compiles_without_syntax_warning(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-W",
                "error::SyntaxWarning",
                "-m",
                "py_compile",
                str(FOUNDATION_FILE),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
