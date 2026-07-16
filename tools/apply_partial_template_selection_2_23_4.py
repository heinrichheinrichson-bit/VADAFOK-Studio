"""Apply VADAFOK Studio 2.23.4 partial template selection refresh."""

from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
from pathlib import Path


OLD_ALL_TEMPLATE_BLOCK = (
    "        for name in sorted(list_templates()):\n"
    "            prefix = \"✓ \" if name == self.card_selected_template.get() else \"\"\n"
    "            ctk.CTkButton(\n"
    "                tlist,\n"
    "                text=prefix + name,\n"
    "                anchor=\"w\",\n"
    "                fg_color=\"#171717\",\n"
    "                hover_color=\"#2C2C2C\",\n"
    "                command=lambda n=name: self.card_select_template(n)\n"
    "            ).pack(fill=\"x\", padx=8, pady=4)\n"
)

NEW_ALL_TEMPLATE_BLOCK = (
    "        self.card_all_templates_frame = ctk.CTkFrame(\n"
    "            tlist,\n"
    "            fg_color=\"transparent\",\n"
    "        )\n"
    "        self.card_all_templates_frame.pack(fill=\"x\", padx=0, pady=0)\n"
    "        self.card_template_buttons = {}\n"
    "        self.card_build_all_template_buttons()\n"
)

NEW_METHODS = (
    "    def card_build_all_template_buttons(self):\n"
    "        frame = getattr(self, \"card_all_templates_frame\", None)\n"
    "        if frame is None:\n"
    "            return\n"
    "\n"
    "        try:\n"
    "            if not frame.winfo_exists():\n"
    "                return\n"
    "        except Exception:\n"
    "            return\n"
    "\n"
    "        for child in frame.winfo_children():\n"
    "            child.destroy()\n"
    "\n"
    "        self.card_template_buttons = {}\n"
    "        for name in sorted(list_templates()):\n"
    "            prefix = \"✓ \" if name == self.card_selected_template.get() else \"\"\n"
    "            button = ctk.CTkButton(\n"
    "                frame,\n"
    "                text=prefix + name,\n"
    "                anchor=\"w\",\n"
    "                fg_color=\"#171717\",\n"
    "                hover_color=\"#2C2C2C\",\n"
    "                command=lambda n=name: self.card_select_template(n),\n"
    "            )\n"
    "            button.pack(fill=\"x\", padx=8, pady=4)\n"
    "            self.card_template_buttons[name] = button\n"
    "\n"
    "    def card_refresh_all_templates(self):\n"
    "        buttons = getattr(self, \"card_template_buttons\", {})\n"
    "        available_names = sorted(list_templates())\n"
    "\n"
    "        if set(buttons) != set(available_names):\n"
    "            self.card_build_all_template_buttons()\n"
    "            return\n"
    "\n"
    "        selected = self.card_selected_template.get()\n"
    "        for name, button in buttons.items():\n"
    "            try:\n"
    "                prefix = \"✓ \" if name == selected else \"\"\n"
    "                button.configure(text=prefix + name)\n"
    "            except Exception:\n"
    "                self.card_build_all_template_buttons()\n"
    "                return\n"
    "\n"
)

OLD_SELECT_METHOD = (
    "    def card_select_template(self, name):\n"
    "        self.card_recent_templates = record_recent_template(name, list_templates())\n"
    "        self.card_selected_template.set(name)\n"
    "        self.card_output_name.set(self.card_default_output_name())\n"
    "        self.card_data_undo_stack = []\n"
    "        self.card_data_redo_stack = []\n"
    "        self.card_creator_preview_image = None\n"
    "        self.card_creator_last_render = None\n"
    "        self.show_card_creator_page()\n"
)

NEW_SELECT_METHOD = (
    "    def card_select_template(self, name):\n"
    "        available_names = list_templates()\n"
    "        if name not in available_names:\n"
    "            return\n"
    "\n"
    "        self.card_recent_templates = record_recent_template(\n"
    "            name, available_names\n"
    "        )\n"
    "        self.card_selected_template.set(name)\n"
    "        self.card_output_name.set(self.card_default_output_name())\n"
    "        self.card_data_undo_stack = []\n"
    "        self.card_data_redo_stack = []\n"
    "        self.card_creator_preview_image = None\n"
    "        self.card_creator_last_render = None\n"
    "\n"
    "        self.card_refresh_recent_templates()\n"
    "        self.card_refresh_all_templates()\n"
    "        self.card_build_form()\n"
    "        self.card_update_preview()\n"
)


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    backup_path = app_path.with_suffix(".py.before_2_23_4.bak")

    if not app_path.is_file():
        raise RuntimeError(f"app.py fehlt: {app_path}")

    original = app_path.read_text(encoding="utf-8")
    updated = original
    changes = []

    if NEW_ALL_TEMPLATE_BLOCK not in updated:
        count = updated.count(OLD_ALL_TEMPLATE_BLOCK)
        if count != 1:
            raise RuntimeError(
                "Erwartet wurde genau ein All-Templates-Block, "
                f"gefunden wurden {count}."
            )
        updated = updated.replace(
            OLD_ALL_TEMPLATE_BLOCK,
            NEW_ALL_TEMPLATE_BLOCK,
            1,
        )
        changes.append("Dedizierter All-Templates-Container")

    if "def card_build_all_template_buttons(self):" not in updated:
        anchor = "    def card_refresh_recent_templates(self):\n"
        if anchor not in updated:
            raise RuntimeError("Recent-Refresh-Methode wurde nicht gefunden.")
        updated = updated.replace(anchor, NEW_METHODS + anchor, 1)
        changes.append("Partielle Auswahlmarkierung")

    if NEW_SELECT_METHOD not in updated:
        count = updated.count(OLD_SELECT_METHOD)
        if count != 1:
            raise RuntimeError(
                "Erwartet wurde genau eine 2.23.3-Auswahlmethode, "
                f"gefunden wurden {count}."
            )
        updated = updated.replace(OLD_SELECT_METHOD, NEW_SELECT_METHOD, 1)
        changes.append("Partielle Template-Auswahl")

    required = (
        "self.card_all_templates_frame = ctk.CTkFrame",
        "self.card_template_buttons = {}",
        "def card_refresh_all_templates(self):",
        "self.card_refresh_recent_templates()",
        "self.card_build_form()",
        "self.card_update_preview()",
    )
    missing = [value for value in required if value not in updated]
    if missing:
        raise RuntimeError(
            "Validierung fehlgeschlagen: " + ", ".join(missing)
        )

    selection_start = updated.index("def card_select_template")
    selection_end = updated.index("def card_template", selection_start)
    selection_method = updated[selection_start:selection_end]
    if "show_card_creator_page" in selection_method:
        raise RuntimeError(
            "Template-Auswahl lädt weiterhin die komplette Seite neu."
        )

    shutil.copy2(app_path, backup_path)
    app_path.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        paths = [
            app_path,
            project_root / "vadafok_studio" / "version.py",
            project_root / "tests" / "test_version.py",
            project_root / "tests" / "test_partial_template_selection.py",
        ]
        for path in paths:
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_partial_template_selection",
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

    print("[OK] Template-Auswahl lädt nicht mehr die komplette Seite.")
    print("[OK] Recent-Markierung wird gezielt aktualisiert.")
    print("[OK] All-Templates-Markierung wird gezielt aktualisiert.")
    print("[OK] Nur Formular und Vorschau werden passend zum Template erneuert.")
    print("[OK] Display Duration und OBS-Status bleiben unangetastet.")
    print("[OK] Python-Syntaxprüfung erfolgreich.")
    if changes:
        print("[GEAENDERT] " + ", ".join(changes))
    print("[FERTIG] VADAFOK Studio 2.23.4 Partial Template Selection angewendet.")


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
