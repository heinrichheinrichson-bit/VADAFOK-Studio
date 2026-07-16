"""Apply VADAFOK Studio 2.24.5.2 Library picker runtime return fix."""

from __future__ import annotations

import ast
import py_compile
import shutil
import subprocess
import sys
import traceback
from pathlib import Path


OPEN_METHOD = (
    "    def open_template_background_picker(self):\n"
    "        self.library_controller.open_template_background_picker()\n"
    "\n"
    "        # Runtime fallbacks remain on the app as well. This guarantees\n"
    "        # correct return behavior even if older Library code resets one\n"
    "        # of the controller compatibility attributes.\n"
    "        self.library_template_background_picker_mode = True\n"
    "        self.library_return_page = \"Template Editor\"\n"
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
    "        controller_return = False\n"
    "        controller = getattr(self, \"library_controller\", None)\n"
    "        if controller is not None:\n"
    "            try:\n"
    "                controller_return = bool(\n"
    "                    controller.complete_template_background_picker()\n"
    "                )\n"
    "            except Exception:\n"
    "                controller_return = False\n"
    "\n"
    "        flag_return = bool(\n"
    "            getattr(\n"
    "                self,\n"
    "                \"library_template_background_picker_mode\",\n"
    "                False,\n"
    "            )\n"
    "        )\n"
    "        page_return = (\n"
    "            getattr(self, \"library_return_page\", None)\n"
    "            == \"Template Editor\"\n"
    "        )\n"
    "\n"
    "        if controller_return or flag_return or page_return:\n"
    "            self.library_template_background_picker_mode = False\n"
    "            self.library_return_page = None\n"
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


def app_class(source):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio":
            return node
    raise RuntimeError("VadafokStudio wurde nicht gefunden.")


def method_node(source, name):
    for node in app_class(source).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise RuntimeError(f"Methode fehlt: {name}")


def replace_method(source, name, replacement):
    node = method_node(source, name)
    lines = source.splitlines(keepends=True)
    lines[node.lineno - 1:node.end_lineno] = [replacement]
    return "".join(lines)


def method_source(source, name):
    node = method_node(source, name)
    return ast.get_source_segment(source, node) or ""


def validate(source):
    open_method = method_source(source, "open_template_background_picker")
    assign = method_source(source, "assign_selected_template_background")
    double_click = method_source(source, "library_item_double_click")
    default_action = method_source(source, "default_selected_action")
    simple_click = method_source(source, "select_library_item")

    required_open = (
        "self.library_controller.open_template_background_picker()",
        "self.library_template_background_picker_mode = True",
        'self.library_return_page = "Template Editor"',
    )
    for item in required_open:
        if item not in open_method:
            raise RuntimeError(f"Picker-Öffnung unvollständig: {item}")

    required_assign = (
        "controller_return",
        "flag_return",
        "page_return",
        "if controller_return or flag_return or page_return:",
        "self.show_template_editor_page()",
    )
    for item in required_assign:
        if item not in assign:
            raise RuntimeError(f"Rückkehrpfad unvollständig: {item}")

    if "self.default_selected_action()" not in double_click:
        raise RuntimeError("Doppelklick verwendet nicht die Standardaktion.")
    if "self.assign_selected_template_background()" not in default_action:
        raise RuntimeError("SHOW / USE führt nicht zur Hintergrundübernahme.")
    if "self.assign_selected_template_background()" in simple_click:
        raise RuntimeError("Einfacher Klick übernimmt weiterhin automatisch.")


def apply(root):
    app = root / "vadafok_studio" / "app.py"
    backup = app.with_suffix(".py.before_2_24_5_2.bak")
    if not app.is_file():
        raise RuntimeError(f"app.py fehlt: {app}")

    original = app.read_text(encoding="utf-8")
    updated = replace_method(
        original,
        "open_template_background_picker",
        OPEN_METHOD,
    )
    updated = replace_method(
        updated,
        "assign_selected_template_background",
        ASSIGN_METHOD,
    )
    validate(updated)

    shutil.copy2(app, backup)
    app.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup.name}")

    try:
        for path in (
            app,
            root / "vadafok_studio" / "version.py",
            root / "tests" / "test_version.py",
            root / "tests" / "test_library_picker_runtime_return.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_library_picker_runtime_return",
                "-v",
            ],
            cwd=root,
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
                f"Runtime-Return-Tests fehlgeschlagen (Exit {result.returncode})."
            )
    except Exception:
        shutil.copy2(backup, app)
        print("[ROLLBACK] app.py wurde automatisch wiederhergestellt.")
        raise

    print("[OK] Doppelklick und SHOW / USE verwenden denselben Rückkehrpfad.")
    print("[OK] Controller-, Flag- und Rückkehrseiten-Signal werden erkannt.")
    print("[OK] Template Editor wird nach Übernahme unmittelbar geöffnet.")
    print("[OK] Einfacher Klick bleibt Auswahl und Vorschau.")
    print("[FERTIG] VADAFOK Studio 2.24.5.2 Runtime Return Fix angewendet.")


def main():
    try:
        apply(Path(__file__).resolve().parent.parent)
    except Exception as exc:
        print("[FEHLER]", exc)
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
