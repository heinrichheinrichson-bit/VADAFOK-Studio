"""Generate PyInstaller Windows version metadata from the central app version."""

from __future__ import annotations

import ast
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_DIR / "vadafok_studio" / "version.py"
OUTPUT_FILE = PROJECT_DIR / "launcher" / "version_info.txt"


def _read_string_constant(name: str) -> str:
    tree = ast.parse(SOURCE_FILE.read_text(encoding="utf-8"), filename=str(SOURCE_FILE))
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                return value.value
            raise ValueError(f"{name} must be a plain string constant in {SOURCE_FILE}")
    raise ValueError(f"{name} was not found in {SOURCE_FILE}")


def _numeric_version(version: str) -> tuple[int, int, int, int]:
    parts = version.split(".")
    if len(parts) != 4 or any(not part.isdigit() for part in parts):
        raise ValueError(
            f"VERSION must contain four numeric parts (for example 2.29.0.1), got: {version!r}"
        )
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def render_version_info(product_name: str, version: str) -> str:
    file_version = _numeric_version(version)
    numeric = ", ".join(str(part) for part in file_version)
    return f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({numeric}),
    prodvers=({numeric}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040704B0',
        [
          StringStruct(u'CompanyName', u'VADAFOK'),
          StringStruct(u'FileDescription', u'{product_name} Windows Launcher'),
          StringStruct(u'FileVersion', u'{version}'),
          StringStruct(u'InternalName', u'{product_name}'),
          StringStruct(u'LegalCopyright', u'Copyright © VADAFOK'),
          StringStruct(u'OriginalFilename', u'{product_name}.exe'),
          StringStruct(u'ProductName', u'{product_name}'),
          StringStruct(u'ProductVersion', u'{version}')
        ]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1031, 1200])])
  ]
)
'''


def main() -> int:
    product_name = _read_string_constant("PRODUCT_NAME")
    version = _read_string_constant("VERSION")
    OUTPUT_FILE.write_text(render_version_info(product_name, version), encoding="utf-8")
    print(f"Launcher version metadata generated: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
