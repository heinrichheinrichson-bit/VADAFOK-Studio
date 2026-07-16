"""Apply-fix for VADAFOK Studio 2.24.2 Template Editor Controller."""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
from pathlib import Path


CONTROLLER_IMPORT = "from .template_editor import TemplateEditorController"
INIT_LINE = (
    "        self.template_editor_controller = "
    "TemplateEditorController(self, list_templates, load_template)"
)

OLD_SELECT_METHOD = (
    "    def template_select(self, name):\n"
    "        self.template_collapsed_groups = set()\n"
    "        self.template_selected_name = name\n"
    "        self.template_selected_field = None\n"
    "        self.template_selected_fields = set()\n"
    "        self.template_working_data = load_template(name)\n"
    "        self.show_template_editor_page()\n"
)

NEW_SELECT_METHOD = (
    "    def template_select(self, name):\n"
    "        self.template_editor_controller.select_template(name)\n"
)


def insert_import(source: str) -> str:
    if CONTROLLER_IMPORT in source:
        return source

    anchor = re.search(
        r"^from \.card_creator import CardCreatorController$",
        source,
        re.MULTILINE,
    )
    if not anchor:
        raise RuntimeError("Card-Creator-Controller-Import wurde nicht gefunden.")

    return source[:anchor.end()] + "\n" + CONTROLLER_IMPORT + source[anchor.end():]


def insert_controller_init(source: str) -> str:
    if INIT_LINE in source:
        return source

    anchor = re.search(
        r'^        self\.template_selected_name\s*=\s*"Default Stream Plan"\s*$',
        source,
        re.MULTILINE,
    )
    if not anchor:
        raise RuntimeError("Template-Editor-Initialisierung wurde nicht gefunden.")

    return source[:anchor.end()] + "\n" + INIT_LINE + source[anchor.end():]


def extract_method(source: str, method_name: str) -> str:
    pattern = re.compile(
        rf"^    def {re.escape(method_name)}\(.*?(?=^    def |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(
            f"{method_name}: erwartet wurde genau eine Methode, gefunden wurden {len(matches)}."
        )
    return matches[0].group(0)


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    controller_path = (
        project_root / "vadafok_studio" / "template_editor" / "controller.py"
    )
    backup_path = app_path.with_suffix(".py.before_2_24_2.bak")

    for path in (app_path, controller_path):
        if not path.is_file():
            raise RuntimeError(f"Benötigte Datei fehlt: {path}")

    original = app_path.read_text(encoding="utf-8")
    updated = insert_import(original)
    updated = insert_controller_init(updated)

    if NEW_SELECT_METHOD not in updated:
        count = updated.count(OLD_SELECT_METHOD)
        if count != 1:
            raise RuntimeError(
                "Erwartet wurde genau eine Template-Auswahlmethode, "
                f"gefunden wurden {count}."
            )
        updated = updated.replace(OLD_SELECT_METHOD, NEW_SELECT_METHOD, 1)

    required = (
        CONTROLLER_IMPORT,
        INIT_LINE,
        "self.template_editor_controller.select_template(name)",
    )
    missing = [value for value in required if value not in updated]
    if missing:
        raise RuntimeError("Validierung fehlgeschlagen: " + ", ".join(missing))

    method = extract_method(updated, "template_select")
    for forbidden in (
        "load_template(name)",
        "show_template_editor_page()",
        "template_selected_field = None",
    ):
        if forbidden in method:
            raise RuntimeError(
                f"Alte Auswahl-Logik noch in template_select vorhanden: {forbidden}"
            )

    shutil.copy2(app_path, backup_path)
    app_path.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        for path in (
            app_path,
            project_root / "vadafok_studio" / "version.py",
            controller_path,
            project_root / "tests" / "test_template_editor_controller.py",
            project_root / "tests" / "test_version.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_template_editor_controller",
                "-v",
            ],
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
        raise RuntimeError(
            "Prüfung fehlgeschlagen. app.py wurde automatisch wiederhergestellt."
        )

    print("[OK] TemplateEditorController integriert.")
    print("[OK] Template-Auswahl aus app.py ausgelagert.")
    print("[OK] Validierung prüft exakt nur template_select().")
    print("[OK] Andere show_template_editor_page()-Aufrufe bleiben unangetastet.")
    print("[OK] Python-Syntaxprüfung erfolgreich.")
    print("[FERTIG] VADAFOK Studio 2.24.2 Template Editor Controller angewendet.")


def main() -> int:
    try:
        apply(Path(__file__).resolve().parent.parent)
    except Exception as exc:
        print(f"[FEHLER] {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
