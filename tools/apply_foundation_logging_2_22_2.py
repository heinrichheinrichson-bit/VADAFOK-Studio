"""Apply VADAFOK Studio 2.22.2 central logging."""

from __future__ import annotations

import py_compile
import shutil
import sys
from pathlib import Path


IMPORT_LINE = "from .logging_setup import LOGGER"
START_LINE = 'LOGGER.info("app.py loaded successfully")'


def _insert_after_version_import(source: str) -> tuple[str, bool]:
    if IMPORT_LINE in source:
        return source, False

    lines = source.splitlines(keepends=True)
    candidate_indexes = [
        index
        for index, line in enumerate(lines)
        if line.startswith("from .version import ")
    ]
    if not candidate_indexes:
        raise RuntimeError(
            "Der Central-Versioning-Import aus 2.22.1 wurde nicht gefunden."
        )

    newline = "\r\n" if "\r\n" in source else "\n"
    insert_at = candidate_indexes[-1] + 1
    lines.insert(insert_at, IMPORT_LINE + newline)
    return "".join(lines), True


def _insert_start_log(source: str) -> tuple[str, bool]:
    if START_LINE in source:
        return source, False

    lines = source.splitlines(keepends=True)
    import_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.strip() == IMPORT_LINE
        ),
        None,
    )
    if import_index is None:
        raise RuntimeError("Logging-Import wurde nicht gefunden.")

    newline = "\r\n" if "\r\n" in source else "\n"
    insert_at = import_index + 1
    lines.insert(insert_at, START_LINE + newline)
    return "".join(lines), True


def _update_gitignore(project_root: Path) -> None:
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("logs/\\n", encoding="utf-8")
        print("[OK] .gitignore erstellt und logs/ eingetragen.")
        return

    text = gitignore.read_text(encoding="utf-8")
    lines = {line.strip() for line in text.splitlines()}
    if "logs/" in lines:
        print("[OK] logs/ ist bereits in .gitignore enthalten.")
        return

    separator = "" if text.endswith(("\\n", "\\r")) else "\\n"
    gitignore.write_text(
        text + separator + "\\n# Runtime logs\\nlogs/\\n",
        encoding="utf-8",
    )
    print("[OK] logs/ zu .gitignore hinzugefügt.")


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    version_path = project_root / "vadafok_studio" / "version.py"
    logging_path = project_root / "vadafok_studio" / "logging_setup.py"
    backup_path = app_path.with_suffix(".py.before_2_22_2.bak")

    for path in (app_path, version_path, logging_path):
        if not path.is_file():
            raise RuntimeError(f"Benötigte Datei fehlt: {path}")

    original = app_path.read_text(encoding="utf-8")
    updated, import_changed = _insert_after_version_import(original)
    updated, log_changed = _insert_start_log(updated)

    required = (
        IMPORT_LINE,
        START_LINE,
        "APP_TITLE",
        "APP_USER_MODEL_ID",
        "SIDEBAR_VERSION",
    )
    missing = [value for value in required if value not in updated]
    if missing:
        raise RuntimeError(
            "Validierung fehlgeschlagen. Nicht gefunden: " + ", ".join(missing)
        )

    if updated != original:
        shutil.copy2(app_path, backup_path)
        app_path.write_text(updated, encoding="utf-8")
        print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")
    else:
        print("[OK] Logging-Integration war bereits vollständig vorhanden.")

    _update_gitignore(project_root)

    try:
        py_compile.compile(str(version_path), doraise=True)
        py_compile.compile(str(logging_path), doraise=True)
        py_compile.compile(str(app_path), doraise=True)
    except Exception:
        if backup_path.exists():
            shutil.copy2(backup_path, app_path)
        raise RuntimeError(
            "Syntaxprüfung fehlgeschlagen. app.py wurde automatisch "
            "wiederhergestellt."
        )

    print("[OK] Zentrales Logging-Modul vorhanden.")
    print("[OK] app.py importiert den zentralen Logger.")
    print("[OK] Startmeldung in app.py integriert.")
    print("[OK] Log-Rotation: 2 MB, 3 Sicherungsdateien.")
    print("[OK] Globale Exception-Hooks installiert.")
    print("[OK] Python-Syntaxprüfung erfolgreich.")

    changed = []
    if import_changed:
        changed.append("Logging-Import")
    if log_changed:
        changed.append("Startmeldung")
    if changed:
        print("[GEAENDERT] " + ", ".join(changed))

    print("[FERTIG] VADAFOK Studio 2.22.2 Foundation Logging angewendet.")


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
