"""Apply VADAFOK Studio 2.24.1 Card Creator Controller extraction."""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
from pathlib import Path

CONTROLLER_IMPORT = "from .card_creator import CardCreatorController"
INIT_LINE = "        self.card_creator_controller = CardCreatorController(self, list_templates)"

REMOVE_DELEGATE = (
    "    def card_remove_recent_template(self, name):\n"
    "        self.card_creator_controller.remove_recent(name)\n"
    "\n"
)

SELECT_DELEGATE = (
    "    def card_select_template(self, name):\n"
    "        self.card_creator_controller.select_template(name)\n"
    "\n"
)


def replace_method(source: str, name: str, next_name: str, replacement: str) -> str:
    pattern = re.compile(
        rf"^    def {re.escape(name)}\(.*?(?=^    def {re.escape(next_name)}\()",
        re.MULTILINE | re.DOTALL,
    )
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(
            f"{name}: erwartet wurde genau eine Methode, gefunden wurden {len(matches)}."
        )
    return pattern.sub(replacement, source, count=1)


def insert_import(source: str) -> str:
    if CONTROLLER_IMPORT in source:
        return source

    anchor = re.search(r"^from \.core\.recent_templates import .+$", source, re.MULTILINE)
    if not anchor:
        raise RuntimeError("Recent-Templates-Import wurde nicht gefunden.")

    return source[:anchor.end()] + "\n" + CONTROLLER_IMPORT + source[anchor.end():]


def insert_controller_init(source: str) -> str:
    if INIT_LINE in source:
        return source

    pattern = re.compile(
        r'^        self\.card_recent_templates\s*=\s*load_recent_templates\(list_templates\(\)\)\s*$',
        re.MULTILINE,
    )
    match = pattern.search(source)
    if not match:
        raise RuntimeError("Card-Creator-Recent-Initialisierung wurde nicht gefunden.")

    replacement = (
        "        self.card_creator_controller = CardCreatorController(self, list_templates)\n"
        "        self.card_recent_templates = self.card_creator_controller.load_recent()"
    )
    return source[:match.start()] + replacement + source[match.end():]


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    controller_path = project_root / "vadafok_studio" / "card_creator" / "controller.py"
    backup_path = app_path.with_suffix(".py.before_2_24_1.bak")

    if not app_path.is_file():
        raise RuntimeError(f"app.py fehlt: {app_path}")
    if not controller_path.is_file():
        raise RuntimeError(f"Controller fehlt: {controller_path}")

    original = app_path.read_text(encoding="utf-8")
    updated = insert_import(original)
    updated = insert_controller_init(updated)
    updated = replace_method(
        updated,
        "card_remove_recent_template",
        "card_select_template",
        REMOVE_DELEGATE,
    )
    updated = replace_method(
        updated,
        "card_select_template",
        "card_template",
        SELECT_DELEGATE,
    )

    required = (
        CONTROLLER_IMPORT,
        "self.card_creator_controller = CardCreatorController",
        "self.card_creator_controller.remove_recent(name)",
        "self.card_creator_controller.select_template(name)",
    )
    missing = [value for value in required if value not in updated]
    if missing:
        raise RuntimeError("Validierung fehlgeschlagen: " + ", ".join(missing))

    for forbidden in (
        "self.show_card_creator_page()",
        "record_recent_template(name, available_names)",
    ):
        start = updated.index("def card_select_template")
        end = updated.index("def card_template", start)
        if forbidden in updated[start:end]:
            raise RuntimeError(f"Alte Auswahl-Logik noch vorhanden: {forbidden}")

    shutil.copy2(app_path, backup_path)
    app_path.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        for path in (
            app_path,
            project_root / "vadafok_studio" / "version.py",
            controller_path,
            project_root / "tests" / "test_card_creator_controller.py",
            project_root / "tests" / "test_version.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [sys.executable, "-m", "unittest", "tests.test_card_creator_controller", "-v"],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)
    except Exception:
        shutil.copy2(backup_path, app_path)
        raise RuntimeError("Prüfung fehlgeschlagen. app.py wurde wiederhergestellt.")

    print("[OK] CardCreatorController integriert.")
    print("[OK] Recent-Entfernen aus app.py ausgelagert.")
    print("[OK] Template-Auswahl-Orchestrierung aus app.py ausgelagert.")
    print("[OK] Partielle Refreshes bleiben erhalten.")
    print("[OK] Syntaxprüfung erfolgreich.")
    print("[FERTIG] VADAFOK Studio 2.24.1 Card Creator Controller angewendet.")


def main() -> int:
    try:
        apply(Path(__file__).resolve().parent.parent)
    except Exception as exc:
        print(f"[FEHLER] {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
