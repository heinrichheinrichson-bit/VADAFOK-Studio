"""Robust, reversible patch for VADAFOK Studio 2.22.1.

The patch updates only runtime version references in vadafok_studio/app.py.
It uses whitespace-tolerant regular expressions, validates exact match counts,
creates a backup, compiles the result and automatically restores on failure.
"""

from __future__ import annotations

import py_compile
import re
import shutil
import sys
from pathlib import Path


IMPORT_LINE = "from .version import APP_TITLE, APP_USER_MODEL_ID, SIDEBAR_VERSION"

TITLE_PATTERN = re.compile(
    r'self\.wm_title\(\s*["\']VADAFOK Studio 2\.16\.5\.1["\']\s*\)'
)
APP_ID_PATTERN = re.compile(
    r'ctypes\.windll\.shell32\.SetCurrentProcessExplicitAppUserModelID'
    r'\(\s*["\']VADAFOK\.Studio\.2\.16\.5\.1["\']\s*\)',
    re.MULTILINE,
)
SIDEBAR_PATTERN = re.compile(
    r'text\s*=\s*["\']Studio 2\.16\.5\.1["\']'
)

TITLE_REPLACEMENT = "self.wm_title(APP_TITLE)"
APP_ID_REPLACEMENT = (
    "ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("
    "APP_USER_MODEL_ID)"
)
SIDEBAR_REPLACEMENT = "text=SIDEBAR_VERSION"


def _insert_import(source: str) -> tuple[str, bool]:
    if IMPORT_LINE in source:
        return source, False

    # Insert after the last top-level relative import. This avoids depending on
    # one specific existing import line.
    lines = source.splitlines(keepends=True)
    relative_import_indexes = [
        index
        for index, line in enumerate(lines)
        if line.startswith("from .")
    ]

    if relative_import_indexes:
        insert_at = relative_import_indexes[-1] + 1
    else:
        # Safe fallback: after the ordinary import block.
        import_indexes = [
            index
            for index, line in enumerate(lines)
            if line.startswith("import ") or line.startswith("from ")
        ]
        if not import_indexes:
            raise RuntimeError("In app.py wurde kein Importblock gefunden.")
        insert_at = import_indexes[-1] + 1

    newline = "\r\n" if "\r\n" in source else "\n"
    lines.insert(insert_at, IMPORT_LINE + newline)
    return "".join(lines), True


def _replace_exactly_once(
    source: str,
    pattern: re.Pattern[str],
    replacement: str,
    label: str,
    already_present: str,
) -> tuple[str, bool]:
    if already_present in source:
        return source, False

    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(
            f"{label}: erwartet wurde genau 1 alte Fundstelle, gefunden wurden "
            f"{len(matches)}."
        )

    return pattern.sub(replacement, source, count=1), True


def _validate(updated: str) -> None:
    required = {
        "Central-Version-Import": IMPORT_LINE,
        "Fenstertitel": "self.wm_title(APP_TITLE)",
        "Windows-App-ID": (
            "SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)"
        ),
        "Sidebar-Version": "text=SIDEBAR_VERSION",
    }

    missing = [label for label, value in required.items() if value not in updated]
    if missing:
        raise RuntimeError(
            "Validierung fehlgeschlagen. Nicht gefunden: " + ", ".join(missing)
        )

    forbidden = (
        "VADAFOK Studio 2.16.5.1",
        "VADAFOK.Studio.2.16.5.1",
        "Studio 2.16.5.1",
    )
    remaining = [value for value in forbidden if value in updated]
    if remaining:
        raise RuntimeError(
            "Alte Laufzeit-Versionen sind noch vorhanden: " + ", ".join(remaining)
        )


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    version_path = project_root / "vadafok_studio" / "version.py"
    backup_path = app_path.with_suffix(".py.before_2_22_1.bak")

    if not app_path.is_file():
        raise RuntimeError(f"app.py wurde nicht gefunden: {app_path}")
    if not version_path.is_file():
        raise RuntimeError(f"version.py wurde nicht gefunden: {version_path}")

    original = app_path.read_text(encoding="utf-8")
    updated = original
    changes: list[str] = []

    updated, changed = _insert_import(updated)
    if changed:
        changes.append("Central-Version-Import")

    updated, changed = _replace_exactly_once(
        updated,
        TITLE_PATTERN,
        TITLE_REPLACEMENT,
        "Fenstertitel",
        "self.wm_title(APP_TITLE)",
    )
    if changed:
        changes.append("Fenstertitel")

    updated, changed = _replace_exactly_once(
        updated,
        APP_ID_PATTERN,
        APP_ID_REPLACEMENT,
        "Windows-App-ID",
        "SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)",
    )
    if changed:
        changes.append("Windows-App-ID")

    updated, changed = _replace_exactly_once(
        updated,
        SIDEBAR_PATTERN,
        SIDEBAR_REPLACEMENT,
        "Sidebar-Version",
        "text=SIDEBAR_VERSION",
    )
    if changed:
        changes.append("Sidebar-Version")

    _validate(updated)

    if updated == original:
        print("[OK] Alle Central-Versioning-Aenderungen waren bereits vorhanden.")
    else:
        shutil.copy2(app_path, backup_path)
        app_path.write_text(updated, encoding="utf-8")
        print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        py_compile.compile(str(version_path), doraise=True)
        py_compile.compile(str(app_path), doraise=True)
    except Exception:
        if backup_path.exists():
            shutil.copy2(backup_path, app_path)
        raise RuntimeError(
            "Python-Syntaxpruefung fehlgeschlagen. app.py wurde automatisch "
            "aus der Sicherheitskopie wiederhergestellt."
        )

    print("[OK] Central-Version-Import vorhanden.")
    print("[OK] Fenstertitel verwendet APP_TITLE.")
    print("[OK] Sidebar verwendet SIDEBAR_VERSION.")
    print("[OK] Windows-App-ID verwendet APP_USER_MODEL_ID.")
    print("[OK] Alte Laufzeit-Version 2.16.5.1 nicht mehr in app.py vorhanden.")
    print("[OK] Python-Syntaxpruefung erfolgreich.")

    if changes:
        print("[GEAENDERT] " + ", ".join(changes))

    print("[FERTIG] VADAFOK Studio 2.22.1 Central Versioning angewendet.")


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent

    try:
        apply(project_root)
    except Exception as exc:
        print(f"[FEHLER] {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
