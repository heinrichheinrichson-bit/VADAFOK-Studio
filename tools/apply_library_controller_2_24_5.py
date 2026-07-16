"""Apply VADAFOK Studio 2.24.5 Library Controller extraction."""

from __future__ import annotations

import ast
import py_compile
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path


IMPORT_LINE = "from .library import LibraryController"
INIT_LINE = "        self.library_controller = LibraryController(self)"

OPEN_DELEGATE = (
    "    def open_template_background_picker(self):\n"
    "        self.library_controller.open_template_background_picker()\n"
)

BUTTON_DELEGATE = (
    "    def template_set_background_from_selected(self):\n"
    "        self.library_controller.open_template_background_picker()\n"
)

ASSIGN_METHOD = (
    "    def assign_selected_template_background(self):\n"
    "        item = getattr(self, \"selected_item\", None)\n"
    "        if item is None:\n"
    "            messagebox.showwarning(\n"
    "                \"Template Background\",\n"
    "                \"Bitte zuerst ein Template-Bild auswählen.\",\n"
    "            )\n"
    "            return\n"
    "\n"
    "        if getattr(item, \"kind\", \"\") != \"image\":\n"
    "            messagebox.showwarning(\n"
    "                \"Template Background\",\n"
    "                \"Bitte ein Bild aus der Library auswählen.\",\n"
    "            )\n"
    "            return\n"
    "\n"
    "        dest = self.template_set_background_path(item.path)\n"
    "\n"
    "        if self.library_controller.complete_template_background_picker():\n"
    "            self.show_template_editor_page()\n"
    "            return dest\n"
    "\n"
    "        messagebox.showinfo(\n"
    "            \"Template Background\",\n"
    "            (\n"
    "                f\"Hintergrundbild gespeichert:\\n\\n\"\n"
    "                f\"Template: {self.template_selected_name}\\n\"\n"
    "                f\"Bild: {Path(item.path).name}\"\n"
    "            ),\n"
    "        )\n"
    "        return dest\n"
)


def method_nodes(source: str) -> dict[str, ast.FunctionDef]:
    tree = ast.parse(source)
    app_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        ),
        None,
    )
    if app_class is None:
        raise RuntimeError("Klasse VadafokStudio wurde nicht gefunden.")

    return {
        node.name: node
        for node in app_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def replace_method(source: str, name: str, replacement: str) -> str:
    nodes = method_nodes(source)
    node = nodes.get(name)
    if node is None:
        raise RuntimeError(f"Methode wurde nicht gefunden: {name}")

    lines = source.splitlines(keepends=True)
    start = node.lineno - 1
    end = node.end_lineno
    lines[start:end] = [replacement]
    return "".join(lines)


def insert_method_before(
    source: str,
    anchor_name: str,
    new_method: str,
) -> str:
    nodes = method_nodes(source)
    anchor = nodes.get(anchor_name)
    if anchor is None:
        raise RuntimeError(f"Methodenanker fehlt: {anchor_name}")

    lines = source.splitlines(keepends=True)
    lines[anchor.lineno - 1:anchor.lineno - 1] = [new_method + "\n"]
    return "".join(lines)


def ensure_open_delegate(source: str) -> str:
    nodes = method_nodes(source)
    if "open_template_background_picker" in nodes:
        return replace_method(
            source,
            "open_template_background_picker",
            OPEN_DELEGATE,
        )

    return insert_method_before(
        source,
        "show_library",
        OPEN_DELEGATE,
    )


def remove_picker_auto_apply(source: str) -> str:
    """Remove earlier experimental one-click block from select_library_item."""
    nodes = method_nodes(source)
    node = nodes.get("select_library_item")
    if node is None:
        raise RuntimeError("select_library_item wurde nicht gefunden.")

    target = None
    for child in node.body:
        if not isinstance(child, ast.If):
            continue
        segment = ast.get_source_segment(source, child) or ""
        if (
            "library_template_background_picker_mode" in segment
            and "assign_selected_template_background" in segment
        ):
            target = child
            break

    if target is None:
        return source

    lines = source.splitlines(keepends=True)
    del lines[target.lineno - 1:target.end_lineno]
    return "".join(lines)


def insert_import(source: str) -> str:
    if IMPORT_LINE in source:
        return source

    candidates = (
        "from .template_editor import TemplateEditorController",
        "from .card_creator import CardCreatorController",
    )
    for anchor in candidates:
        match = re.search(
            rf"^{re.escape(anchor)}$",
            source,
            re.MULTILINE,
        )
        if match:
            return (
                source[:match.end()]
                + "\n"
                + IMPORT_LINE
                + source[match.end():]
            )

    raise RuntimeError("Controller-Import-Anker wurde nicht gefunden.")


def insert_init(source: str) -> str:
    if INIT_LINE in source:
        return source

    anchors = (
        r'^        self\.library_return_page\s*=\s*None\s*$',
        r'^        self\.library_banner_picker_mode\s*=\s*False\s*$',
    )
    for pattern in anchors:
        match = re.search(pattern, source, re.MULTILINE)
        if match:
            return (
                source[:match.end()]
                + "\n"
                + INIT_LINE
                + source[match.end():]
            )

    raise RuntimeError("Library-Initialisierungsanker wurde nicht gefunden.")


def validate(source: str) -> None:
    required = (
        IMPORT_LINE,
        INIT_LINE,
        "self.library_controller.open_template_background_picker()",
        "self.library_controller.complete_template_background_picker()",
        "self.show_template_editor_page()",
    )
    missing = [item for item in required if item not in source]
    if missing:
        raise RuntimeError(
            "Validierung fehlgeschlagen: " + ", ".join(missing)
        )

    nodes = method_nodes(source)

    select = ast.get_source_segment(
        source,
        nodes["select_library_item"],
    ) or ""
    if "self.assign_selected_template_background()" in select:
        raise RuntimeError(
            "Einfacher Klick enthält weiterhin automatische Übernahme."
        )

    double_click = ast.get_source_segment(
        source,
        nodes["library_item_double_click"],
    ) or ""
    if "self.default_selected_action()" not in double_click:
        raise RuntimeError(
            "Doppelklick verwendet nicht mehr die Standardaktion."
        )


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    controller_path = (
        project_root / "vadafok_studio" / "library" / "controller.py"
    )
    backup_path = app_path.with_suffix(".py.before_2_24_5.bak")

    for path in (app_path, controller_path):
        if not path.is_file():
            raise RuntimeError(f"Benötigte Datei fehlt: {path}")

    original = app_path.read_text(encoding="utf-8")
    updated = insert_import(original)
    updated = insert_init(updated)
    updated = ensure_open_delegate(updated)
    updated = replace_method(
        updated,
        "template_set_background_from_selected",
        BUTTON_DELEGATE,
    )
    updated = replace_method(
        updated,
        "assign_selected_template_background",
        ASSIGN_METHOD,
    )
    updated = remove_picker_auto_apply(updated)

    validate(updated)

    shutil.copy2(app_path, backup_path)
    app_path.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        for path in (
            app_path,
            project_root / "vadafok_studio" / "version.py",
            controller_path,
            project_root / "tests" / "test_library_controller.py",
            project_root / "tests" / "test_library_controller_integration.py",
            project_root / "tests" / "test_version.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_library_controller",
                "tests.test_library_controller_integration",
                "-v",
            ],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                "Automatische Library-Controller-Tests fehlgeschlagen "
                f"(Exit-Code {result.returncode})."
            )
    except Exception:
        shutil.copy2(backup_path, app_path)
        print("[ROLLBACK] app.py wurde automatisch wiederhergestellt.")
        raise

    print("[OK] LibraryController integriert.")
    print("[OK] Picker-Zustand liegt außerhalb der neu aufgebauten Library-Seite.")
    print("[OK] Einfacher Klick bleibt Auswahl und Vorschau.")
    print("[OK] Doppelklick verwendet weiterhin SHOW / USE-Standardaktion.")
    print("[OK] SHOW / USE übernimmt und kehrt im Picker-Modus zurück.")
    print("[OK] Normaler Library-Betrieb bleibt unverändert.")
    print("[OK] Python-Syntaxprüfung erfolgreich.")
    print("[FERTIG] VADAFOK Studio 2.24.5 Library Controller angewendet.")


def main() -> int:
    try:
        apply(Path(__file__).resolve().parent.parent)
    except Exception as exc:
        print()
        print("[FEHLER]", exc)
        print()
        print("Vollständiger Traceback:")
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
