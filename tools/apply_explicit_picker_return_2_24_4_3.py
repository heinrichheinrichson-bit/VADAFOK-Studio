"""Apply VADAFOK Studio 2.24.4.3 explicit Template picker return."""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path


OPEN_METHOD = (
    "    def open_template_background_picker(self):\n"
    "        self.library_template_background_picker_mode = True\n"
    "        self.library_return_page = \"Template Editor\"\n"
    "        self.show_library()\n"
    "        self.open_library_section(\"Templates\")\n"
    "\n"
    "        if hasattr(self, \"library_info\"):\n"
    "            self.library_info.configure(\n"
    "                text=(\n"
    "                    \"TEMPLATE BACKGROUND PICKER — Einfacher Klick zeigt \"\n"
    "                    \"die Vorschau. Doppelklick oder USE SELECTED & BACK \"\n"
    "                    \"übernimmt das Bild.\"\n"
    "                ),\n"
    "                text_color=GOLD,\n"
    "            )\n"
    "\n"
)

RETURN_METHOD = (
    "    def return_to_template_editor_from_library(self):\n"
    "        item = getattr(self, \"selected_item\", None)\n"
    "        if item is None or getattr(item, \"kind\", \"\") != \"image\":\n"
    "            messagebox.showwarning(\n"
    "                \"Template Background\",\n"
    "                \"Bitte zuerst ein Template-Bild auswählen.\",\n"
    "            )\n"
    "            return\n"
    "\n"
    "        self.assign_selected_template_background()\n"
    "\n"
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


def replace_method(source, name, replacement):
    pattern = re.compile(
        rf"^    def {re.escape(name)}\(.*?(?=^    def |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(
            f"{name}: erwartet 1 Methode, gefunden {len(matches)}."
        )
    m = matches[0]
    return source[:m.start()] + replacement + source[m.end():]


def insert_return_method(source):
    if "def return_to_template_editor_from_library(self):" in source:
        return replace_method(
            source,
            "return_to_template_editor_from_library",
            RETURN_METHOD,
        )

    marker = re.search(
        r"^    def show_library\(self\):",
        source,
        re.MULTILINE,
    )
    if not marker:
        raise RuntimeError("show_library wurde nicht gefunden.")
    return source[:marker.start()] + RETURN_METHOD + source[marker.start():]


def add_picker_button(source):
    marker = (
        "        self.library_info = ctk.CTkLabel(\n"
    )
    if "USE SELECTED & BACK TO TEMPLATE EDITOR" in source:
        return source

    idx = source.find(marker, source.index("def show_library"))
    if idx < 0:
        raise RuntimeError("Library-Info-Anker wurde nicht gefunden.")

    block = (
        "        if getattr(\n"
        "            self,\n"
        "            \"library_template_background_picker_mode\",\n"
        "            False,\n"
        "        ):\n"
        "            ctk.CTkButton(\n"
        "                top,\n"
        "                text=\"USE SELECTED & BACK TO TEMPLATE EDITOR\",\n"
        "                width=245,\n"
        "                fg_color=GOLD,\n"
        "                text_color=\"#111111\",\n"
        "                hover_color=GOLD_DARK,\n"
        "                command=self.return_to_template_editor_from_library,\n"
        "            ).grid(row=0, column=6, padx=(8, 0))\n"
        "\n"
    )
    return source[:idx] + block + source[idx:]


def validate(source):
    required = (
        "def open_template_background_picker(self):",
        "def return_to_template_editor_from_library(self):",
        "USE SELECTED & BACK TO TEMPLATE EDITOR",
        "command=self.return_to_template_editor_from_library",
        "self.assign_selected_template_background()",
        "self.library_template_background_picker_mode = False",
        "self.show_template_editor_page()",
    )
    missing = [x for x in required if x not in source]
    if missing:
        raise RuntimeError("Validierung fehlgeschlagen: " + ", ".join(missing))


def apply(root):
    app = root / "vadafok_studio" / "app.py"
    backup = app.with_suffix(".py.before_2_24_4_3.bak")
    if not app.is_file():
        raise RuntimeError(f"app.py fehlt: {app}")

    original = app.read_text(encoding="utf-8")
    updated = replace_method(
        original,
        "open_template_background_picker",
        OPEN_METHOD,
    )
    updated = insert_return_method(updated)
    updated = replace_method(
        updated,
        "assign_selected_template_background",
        ASSIGN_METHOD,
    )
    updated = add_picker_button(updated)
    validate(updated)

    shutil.copy2(app, backup)
    app.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup.name}")

    try:
        for path in (
            app,
            root / "vadafok_studio" / "version.py",
            root / "tests" / "test_version.py",
            root / "tests" / "test_explicit_template_picker_return.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_explicit_template_picker_return",
                "-v",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        if result.returncode != 0:
            raise RuntimeError(
                f"Picker-Tests fehlgeschlagen (Exit {result.returncode})."
            )
    except Exception:
        shutil.copy2(backup, app)
        print("[ROLLBACK] app.py wurde wiederhergestellt.")
        raise

    print("[OK] Einfacher Klick bleibt Auswahl/Vorschau.")
    print("[OK] Doppelklick übernimmt und kehrt zurück.")
    print("[OK] Expliziter USE-&-BACK-Button integriert.")
    print("[OK] Normaler Library-Betrieb bleibt unverändert.")
    print("[FERTIG] VADAFOK Studio 2.24.4.3 Explicit Picker Return angewendet.")


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
