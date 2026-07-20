from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
VERSION_SOURCE = PROJECT_DIR / "vadafok_studio" / "version.py"
GENERATOR_SOURCE = PROJECT_DIR / "launcher" / "generate_version_info.py"


def _constant(name: str) -> str:
    tree = ast.parse(VERSION_SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                assert isinstance(node.value, ast.Constant)
                assert isinstance(node.value.value, str)
                return node.value.value
    raise AssertionError(f"Missing constant: {name}")


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_version_info", GENERATOR_SOURCE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_application_version_has_four_numeric_parts() -> None:
    version = _constant("VERSION")
    parts = version.split(".")
    assert len(parts) == 4
    assert all(part.isdigit() for part in parts)


def test_launcher_metadata_uses_central_version() -> None:
    generator = _load_generator()
    version = _constant("VERSION")
    product_name = _constant("PRODUCT_NAME")
    rendered = generator.render_version_info(product_name, version)

    assert f"FileVersion', u'{version}'" in rendered
    assert f"ProductVersion', u'{version}'" in rendered
    tuple_text = ", ".join(version.split("."))
    assert f"filevers=({tuple_text})" in rendered
    assert f"prodvers=({tuple_text})" in rendered
