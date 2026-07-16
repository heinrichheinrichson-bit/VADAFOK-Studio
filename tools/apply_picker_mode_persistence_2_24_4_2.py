"""Apply VADAFOK Studio 2.24.4.2 picker mode persistence fix."""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path


NEW_OPEN_METHOD = (
    "    def open_template_background_picker(self):\n"
    "        self.show_library()\n"
    "        self.open_library_section(\"Templates\")\n"
    "\n"
    "        # show_library() may rebuild/reset Library state. Therefore the\n"
    "        # picker flags must be set only after the Library is fully built.\n"
    "        self.library_template_background_picker_mode = True\n"
    "        self.library_return_page = \"Template Editor\"\n"
    "\n"
    "        if hasattr(self, \"library_info\"):\n"
    "            self.library_info.configure(\n"
    "                text=(\n"
    "                    \"TEMPLATE BACKGROUND PICKER — Bild anklicken. \"\n"
    "                    \"Es wird sofort übernommen und der Template Editor \"\n"
    "                    \"öffnet sich wieder.\"\n"
    "                ),\n"
    "                text_color=GOLD,\n"
    "            )\n"
    "\n"
    "        if hasattr(self, \"selection_meta\"):\n"
    "            self.selection_meta.configure(\n"
    "                text=(\n"
    "                    \"Ein Klick auf ein Bild übernimmt es sofort als \"\n"
    "                    \"Template-Hintergrund.\"\n"
    "                )\n"
    "            )\n"
    "\n"
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
    "\n"
    "        picker_mode = bool(\n"
    "            getattr(\n"
    "                self,\n"
    "                \"library_template_background_picker_mode\",\n"
    "                False,\n"
    "            )\n"
    "            or getattr(self, \"library_return_page\", None)\n"
    "            == \"Template Editor\"\n"
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
) -> str:
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

    return (
        source[:matches[0].start()]
        + replacement
        + source[matches[0].end():]
    )


def validate(source: str) -> None:
    open_start = source.index("def open_template_background_picker")
    open_end = source.index("def show_library", open_start)
    open_method = source[open_start:open_end]

    show_index = open_method.index("self.show_library()")
    section_index = open_method.index(
        'self.open_library_section("Templates")'
    )
    mode_index = open_method.rindex(
        "self.library_template_background_picker_mode = True"
    )

    if mode_index <= show_index or mode_index <= section_index:
        raise RuntimeError(
            "Picker-Modus wird weiterhin zu früh aktiviert."
        )

    assign_start = source.index(
        "def assign_selected_template_background"
    )
    assign_tail = source[assign_start:]
    next_method = assign_tail.find("\n    def ", 1)
    assign_method = (
        assign_tail if next_method < 0 else assign_tail[:next_method]
    )

    required = (
        "library_template_background_picker_mode",
        'library_return_page", None)',
        '== "Template Editor"',
        "self.show_template_editor_page()",
    )
    missing = [item for item in required if item not in assign_method]
    if missing:
        raise RuntimeError(
            "Picker-Rückkehr-Validierung fehlgeschlagen: "
            + ", ".join(missing)
        )


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    backup_path = app_path.with_suffix(".py.before_2_24_4_2.bak")

    if not app_path.is_file():
        raise RuntimeError(f"app.py fehlt: {app_path}")

    original = app_path.read_text(encoding="utf-8")
    updated = replace_method(
        original,
        "open_template_background_picker",
        NEW_OPEN_METHOD,
    )
    updated = replace_method(
        updated,
        "assign_selected_template_background",
        NEW_ASSIGN_METHOD,
    )

    validate(updated)

    shutil.copy2(app_path, backup_path)
    app_path.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        for path in (
            app_path,
            project_root / "vadafok_studio" / "version.py",
            project_root / "tests" / "test_version.py",
            project_root / "tests" / "test_picker_mode_persistence.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_picker_mode_persistence",
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
                "Automatische Picker-Persistenztests fehlgeschlagen "
                f"(Exit-Code {result.returncode})."
            )
    except Exception:
        shutil.copy2(backup_path, app_path)
        print("[ROLLBACK] app.py wurde automatisch wiederhergestellt.")
        raise

    print("[OK] Picker-Modus wird nach dem Library-Aufbau aktiviert.")
    print("[OK] Rückkehrziel Template Editor bleibt erhalten.")
    print("[OK] Klick, Doppelklick und SHOW / USE erkennen den Picker-Modus.")
    print("[OK] Automatische Rückkehr zum Template Editor ist abgesichert.")
    print("[OK] Normaler Library-Betrieb bleibt unverändert.")
    print("[FERTIG] VADAFOK Studio 2.24.4.2 Picker Mode Persistence Fix angewendet.")


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
