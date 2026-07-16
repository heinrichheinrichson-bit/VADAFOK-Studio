"""Apply VADAFOK Studio 2.24.4 visual Library background picker."""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path


OPEN_PICKER_METHOD = (
    "    def open_template_background_picker(self):\n"
    "        self.library_template_background_picker_mode = True\n"
    "        self.library_return_page = \"Template Editor\"\n"
    "        self.show_library()\n"
    "        self.open_library_section(\"Templates\")\n"
    "\n"
    "        if hasattr(self, \"library_info\"):\n"
    "            self.library_info.configure(\n"
    "                text=(\n"
    "                    \"TEMPLATE BACKGROUND PICKER — Bild anklicken für die \"\n"
    "                    \"große Vorschau. SHOW / USE oder Doppelklick übernimmt \"\n"
    "                    \"es als Hintergrund.\"\n"
    "                ),\n"
    "                text_color=GOLD,\n"
    "            )\n"
    "\n"
    "        if hasattr(self, \"selection_meta\"):\n"
    "            self.selection_meta.configure(\n"
    "                text=(\n"
    "                    \"Wähle links ein Template-Bild. \"\n"
    "                    \"SHOW / USE übernimmt es und kehrt zum Editor zurück.\"\n"
    "                )\n"
    "            )\n"
    "\n"
)

NEW_BUTTON_METHOD = (
    "    def template_set_background_from_selected(self):\n"
    "        self.open_template_background_picker()\n"
)

NEW_ASSIGN_METHOD = (
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
    "        picker_mode = bool(\n"
    "            getattr(\n"
    "                self,\n"
    "                \"library_template_background_picker_mode\",\n"
    "                False,\n"
    "            )\n"
    "        )\n"
    "\n"
    "        if picker_mode:\n"
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


def replace_method(
    source: str,
    method_name: str,
    replacement: str,
) -> tuple[str, bool]:
    pattern = re.compile(
        rf"^    def {re.escape(method_name)}\(.*?(?=^    def |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(
            f"{method_name}: erwartet wurde genau eine Methode, "
            f"gefunden wurden {len(matches)}."
        )

    current = matches[0].group(0)
    if current == replacement:
        return source, False

    return (
        source[:matches[0].start()]
        + replacement
        + source[matches[0].end():],
        True,
    )


def insert_picker_method(source: str) -> tuple[str, bool]:
    if "def open_template_background_picker(self):" in source:
        return source, False

    anchor = re.search(
        r"^    def show_library\(self\):",
        source,
        re.MULTILINE,
    )
    if not anchor:
        raise RuntimeError("show_library wurde nicht gefunden.")

    return (
        source[:anchor.start()]
        + OPEN_PICKER_METHOD
        + source[anchor.start():],
        True,
    )


def add_cancel_reset(source: str) -> tuple[str, bool]:
    pattern = re.compile(
        r"(^    def show_template_editor_page\(self\):\s*\n)",
        re.MULTILINE,
    )
    match = pattern.search(source)
    if not match:
        raise RuntimeError("show_template_editor_page wurde nicht gefunden.")

    reset_line = (
        "        self.library_template_background_picker_mode = False\n"
    )

    method_start = match.end()
    method_tail = source[method_start:method_start + 300]
    if reset_line.strip() in method_tail:
        return source, False

    return (
        source[:match.end()]
        + reset_line
        + source[match.end():],
        True,
    )


def validate(source: str) -> None:
    required = (
        "def open_template_background_picker(self):",
        "self.library_template_background_picker_mode = True",
        'self.open_library_section("Templates")',
        "self.open_template_background_picker()",
        "library_template_background_picker_mode",
        "self.show_template_editor_page()",
    )
    missing = [value for value in required if value not in source]
    if missing:
        raise RuntimeError(
            "Validierung fehlgeschlagen: " + ", ".join(missing)
        )

    button_pattern = re.compile(
        r"^    def template_set_background_from_selected"
        r"\(self\):.*?(?=^    def |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    button_method = button_pattern.search(source)
    if not button_method:
        raise RuntimeError(
            "template_set_background_from_selected fehlt nach dem Patch."
        )

    if "assign_selected_template_background()" in button_method.group(0):
        raise RuntimeError(
            "Der Button verwendet weiterhin die alte Vorselektion."
        )


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    backup_path = app_path.with_suffix(".py.before_2_24_4.bak")

    if not app_path.is_file():
        raise RuntimeError(f"app.py fehlt: {app_path}")

    original = app_path.read_text(encoding="utf-8")
    updated = original
    changes: list[str] = []

    updated, changed = insert_picker_method(updated)
    if changed:
        changes.append("Visual-Picker-Einstieg")

    updated, changed = replace_method(
        updated,
        "template_set_background_from_selected",
        NEW_BUTTON_METHOD,
    )
    if changed:
        changes.append("Template-Editor-Button")

    updated, changed = replace_method(
        updated,
        "assign_selected_template_background",
        NEW_ASSIGN_METHOD,
    )
    if changed:
        changes.append("Übernehmen-und-Zurückkehren")

    updated, changed = add_cancel_reset(updated)
    if changed:
        changes.append("Picker-Abbruch")

    validate(updated)

    shutil.copy2(app_path, backup_path)
    app_path.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        paths = [
            app_path,
            project_root / "vadafok_studio" / "version.py",
            project_root / "tests" / "test_version.py",
            project_root / "tests" / "test_template_background_picker.py",
        ]
        for path in paths:
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_template_background_picker",
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
                "Automatische Picker-Tests fehlgeschlagen "
                f"(Exit-Code {result.returncode})."
            )
    except Exception:
        shutil.copy2(backup_path, app_path)
        print("[ROLLBACK] app.py wurde automatisch wiederhergestellt.")
        raise

    print("[OK] Button öffnet Library direkt im Ordner Templates.")
    print("[OK] Bestehende Thumbnail- und Vorschauansicht wird verwendet.")
    print("[OK] SHOW / USE und Doppelklick übernehmen das Bild.")
    print("[OK] Nach Übernahme erfolgt die Rückkehr zum Template Editor.")
    print("[OK] Rückkehr per Sidebar beendet den Picker-Modus.")
    print("[OK] Normaler Library-Betrieb bleibt unverändert.")
    print("[OK] Python-Syntaxprüfung erfolgreich.")
    if changes:
        print("[GEAENDERT] " + ", ".join(changes))
    print(
        "[FERTIG] VADAFOK Studio 2.24.4 "
        "Visual Library Background Picker angewendet."
    )


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
