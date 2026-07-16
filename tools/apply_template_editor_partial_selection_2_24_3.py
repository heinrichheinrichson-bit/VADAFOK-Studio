"""Apply VADAFOK Studio 2.24.3 Template Editor partial selection refresh.

This corrected apply script prints full traceback and test output on failure.
"""

from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
import traceback
from pathlib import Path


OLD_TEMPLATE_LIST = (
    "        default_template_name = get_default_template()\n"
    "        for name in sorted(list_templates()):\n"
    "            prefix = \"✓ \" if name == self.template_selected_name else \"\"\n"
    "            if name == default_template_name:\n"
    "                prefix += \"★ \"\n"
    "            ctk.CTkButton(\n"
    "                template_list,\n"
    "                text=prefix + name,\n"
    "                anchor=\"w\",\n"
    "                fg_color=\"#171717\",\n"
    "                hover_color=\"#2C2C2C\",\n"
    "                command=lambda n=name: self.template_select(n)\n"
    "            ).pack(fill=\"x\", padx=8, pady=4)\n"
)

NEW_TEMPLATE_LIST = (
    "        default_template_name = get_default_template()\n"
    "        self.template_list_buttons = {}\n"
    "        for name in sorted(list_templates()):\n"
    "            prefix = \"✓ \" if name == self.template_selected_name else \"\"\n"
    "            if name == default_template_name:\n"
    "                prefix += \"★ \"\n"
    "            button = ctk.CTkButton(\n"
    "                template_list,\n"
    "                text=prefix + name,\n"
    "                anchor=\"w\",\n"
    "                fg_color=\"#171717\",\n"
    "                hover_color=\"#2C2C2C\",\n"
    "                command=lambda n=name: self.template_select(n)\n"
    "            )\n"
    "            button.pack(fill=\"x\", padx=8, pady=4)\n"
    "            self.template_list_buttons[name] = button\n"
)

REFRESH_METHODS = (
    "    def template_refresh_template_list_selection(self):\n"
    "        buttons = getattr(self, \"template_list_buttons\", {})\n"
    "        available = sorted(list_templates())\n"
    "\n"
    "        if set(buttons) != set(available):\n"
    "            return False\n"
    "\n"
    "        default_name = get_default_template()\n"
    "        for name, button in buttons.items():\n"
    "            prefix = \"✓ \" if name == self.template_selected_name else \"\"\n"
    "            if name == default_name:\n"
    "                prefix += \"★ \"\n"
    "            try:\n"
    "                button.configure(text=prefix + name)\n"
    "            except Exception:\n"
    "                return False\n"
    "\n"
    "        return True\n"
    "\n"
    "    def template_refresh_selected_template(self):\n"
    "        self.template_refresh_template_list_selection()\n"
    "\n"
    "        status_label = getattr(self, \"template_status_label\", None)\n"
    "        if status_label is not None:\n"
    "            try:\n"
    "                status_label.configure(text=self.template_selected_name)\n"
    "            except Exception:\n"
    "                pass\n"
    "\n"
    "        self.template_build_properties_panel()\n"
    "        self.template_ensure_field_ids()\n"
    "        self.template_draw_canvas()\n"
    "        self.template_build_style_presets_panel()\n"
    "        self.template_build_layers_panel()\n"
    "\n"
)


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    controller_path = (
        project_root / "vadafok_studio" / "template_editor" / "controller.py"
    )
    backup_path = app_path.with_suffix(".py.before_2_24_3.bak")

    for path in (app_path, controller_path):
        if not path.is_file():
            raise RuntimeError(f"Benötigte Datei fehlt: {path}")

    original = app_path.read_text(encoding="utf-8")
    updated = original
    changes = []

    if NEW_TEMPLATE_LIST not in updated:
        count = updated.count(OLD_TEMPLATE_LIST)
        if count != 1:
            raise RuntimeError(
                "Erwartet wurde genau eine Template-Listen-Erstellung, "
                f"gefunden wurden {count}."
            )
        updated = updated.replace(OLD_TEMPLATE_LIST, NEW_TEMPLATE_LIST, 1)
        changes.append("Template-Button-Registry")

    if "def template_refresh_selected_template(self):" not in updated:
        anchor = "    def template_build_properties_panel(self):\n"
        if anchor not in updated:
            raise RuntimeError(
                "Anker template_build_properties_panel wurde nicht gefunden."
            )
        updated = updated.replace(anchor, REFRESH_METHODS + anchor, 1)
        changes.append("Partial-Refresh-Methoden")

    required = (
        "self.template_list_buttons = {}",
        "self.template_list_buttons[name] = button",
        "def template_refresh_template_list_selection(self):",
        "def template_refresh_selected_template(self):",
        "self.template_draw_canvas()",
        "self.template_build_layers_panel()",
    )
    missing = [value for value in required if value not in updated]
    if missing:
        raise RuntimeError(
            "Validierung fehlgeschlagen: " + ", ".join(missing)
        )

    refresh_start = updated.index(
        "def template_refresh_selected_template"
    )
    refresh_end = updated.index(
        "def template_build_properties_panel",
        refresh_start,
    )
    refresh_method = updated[refresh_start:refresh_end]
    for forbidden in ("show_template_editor_page", "clear_main"):
        if forbidden in refresh_method:
            raise RuntimeError(
                f"Partial Refresh enthält vollständigen Seitenaufbau: {forbidden}"
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
            project_root / "tests" / "test_template_editor_partial_refresh.py",
            project_root / "tests" / "test_version.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_template_editor_controller",
                "tests.test_template_editor_partial_refresh",
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
                "Automatische Teiltests fehlgeschlagen "
                f"(Exit-Code {result.returncode})."
            )
    except Exception:
        shutil.copy2(backup_path, app_path)
        print("[ROLLBACK] app.py wurde automatisch wiederhergestellt.")
        raise

    print("[OK] Template-Buttons werden wiederverwendet.")
    print("[OK] Template-Markierung wird gezielt aktualisiert.")
    print("[OK] Canvas, Layers und Properties werden gezielt aktualisiert.")
    print("[OK] Kein vollständiger Seitenaufbau beim Templatewechsel.")
    print("[OK] Zoom und übrige UI bleiben erhalten.")
    print("[OK] Python-Syntaxprüfung erfolgreich.")
    if changes:
        print("[GEAENDERT] " + ", ".join(changes))
    print("[FERTIG] VADAFOK Studio 2.24.3 Partial Template Selection angewendet.")


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
