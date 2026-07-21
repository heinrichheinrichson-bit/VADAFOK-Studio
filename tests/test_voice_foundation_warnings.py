from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
import tempfile
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
        # Write outside __pycache__: a running VADAFOK instance can hold the
        # regular Windows bytecode file open while this suite is executed.
        with tempfile.TemporaryDirectory() as folder:
            compiled = str(Path(folder) / "foundation.pyc")
            result = subprocess.run(
                [
                    sys.executable,
                    "-W",
                    "error::SyntaxWarning",
                    "-c",
                    (
                        "import py_compile,sys; "
                        "py_compile.compile(sys.argv[1], cfile=sys.argv[2], doraise=True)"
                    ),
                    str(FOUNDATION_FILE),
                    compiled,
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
