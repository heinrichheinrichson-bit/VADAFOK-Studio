"""Apply VADAFOK Studio 2.23.2 Manage Recent Templates."""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
from pathlib import Path

OLD_IMPORT = "from .core.recent_templates import load_recent_templates, record_recent_template"
NEW_IMPORT = (
    "from .core.recent_templates import "
    "load_recent_templates, record_recent_template, remove_recent_template"
)

REMOVE_METHOD = (
    "    def card_remove_recent_template(self, name):\n"
    "        self.card_recent_templates = remove_recent_template(\n"
    "            name, list_templates()\n"
    "        )\n"
    "        self.show_card_creator_page()\n"
    "\n"
)

OLD_RECENT_LOOP = (
    "            for recent_name in recent_names:\n"
    "                prefix = \"✓ \" if recent_name == self.card_selected_template.get() else \"↶ \"\n"
    "                ctk.CTkButton(\n"
    "                    tlist,\n"
    "                    text=prefix + recent_name,\n"
    "                    anchor=\"w\",\n"
    "                    fg_color=\"#3A2A0D\",\n"
    "                    hover_color=\"#5A4318\",\n"
    "                    command=lambda n=recent_name: self.card_select_template(n),\n"
    "                ).pack(fill=\"x\", padx=8, pady=3)\n"
)

NEW_RECENT_LOOP = (
    "            for recent_name in recent_names:\n"
    "                recent_row = ctk.CTkFrame(tlist, fg_color=\"transparent\")\n"
    "                recent_row.pack(fill=\"x\", padx=8, pady=3)\n"
    "                recent_row.grid_columnconfigure(0, weight=1)\n"
    "\n"
    "                prefix = \"✓ \" if recent_name == self.card_selected_template.get() else \"↶ \"\n"
    "                ctk.CTkButton(\n"
    "                    recent_row,\n"
    "                    text=prefix + recent_name,\n"
    "                    anchor=\"w\",\n"
    "                    fg_color=\"#3A2A0D\",\n"
    "                    hover_color=\"#5A4318\",\n"
    "                    command=lambda n=recent_name: self.card_select_template(n),\n"
    "                ).grid(row=0, column=0, sticky=\"ew\", padx=(0, 4))\n"
    "\n"
    "                ctk.CTkButton(\n"
    "                    recent_row,\n"
    "                    text=\"✕\",\n"
    "                    width=28,\n"
    "                    fg_color=\"#5A2424\",\n"
    "                    hover_color=\"#7A3030\",\n"
    "                    command=lambda n=recent_name: self.card_remove_recent_template(n),\n"
    "                ).grid(row=0, column=1)\n"
)


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    backup_path = app_path.with_suffix(".py.before_2_23_2.bak")
    original = app_path.read_text(encoding="utf-8")
    updated = original
    changes = []

    if NEW_IMPORT not in updated:
        if OLD_IMPORT not in updated:
            raise RuntimeError("Recent-Templates-Import aus 2.23.1 wurde nicht gefunden.")
        updated = updated.replace(OLD_IMPORT, NEW_IMPORT, 1)
        changes.append("Remove-Import")

    if REMOVE_METHOD.strip() not in updated:
        match = re.search(
            r'(^\s*def card_select_template\(self,\s*name\):\s*$)',
            updated,
            flags=re.MULTILINE,
        )
        if not match:
            raise RuntimeError("card_select_template wurde nicht gefunden.")
        updated = updated[:match.start()] + REMOVE_METHOD + updated[match.start():]
        changes.append("Remove-Methode")

    if NEW_RECENT_LOOP not in updated:
        count = updated.count(OLD_RECENT_LOOP)
        if count != 1:
            raise RuntimeError(
                f"Erwartet wurde genau eine Recent-UI-Schleife, gefunden wurden {count}."
            )
        updated = updated.replace(OLD_RECENT_LOOP, NEW_RECENT_LOOP, 1)
        changes.append("X-Buttons")

    for required in (
        NEW_IMPORT,
        "def card_remove_recent_template",
        'text="✕"',
        "remove_recent_template(",
    ):
        if required not in updated:
            raise RuntimeError(f"Validierung fehlgeschlagen: {required}")

    if updated != original:
        shutil.copy2(app_path, backup_path)
        app_path.write_text(updated, encoding="utf-8")
        print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")
    else:
        print("[OK] Manage Recent Templates war bereits integriert.")

    try:
        for path in (
            app_path,
            project_root / "vadafok_studio" / "version.py",
            project_root / "vadafok_studio" / "core" / "recent_templates.py",
            project_root / "tests" / "test_recent_templates.py",
            project_root / "tests" / "test_version.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [sys.executable, "-m", "unittest", "tests.test_recent_templates", "-v"],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)
    except Exception:
        if backup_path.exists():
            shutil.copy2(backup_path, app_path)
        raise RuntimeError("Prüfung fehlgeschlagen. app.py wurde wiederhergestellt.")

    print("[OK] X-Button je Recent-Eintrag integriert.")
    print("[OK] Entfernen betrifft nur den Verlauf.")
    print("[OK] Templates bleiben unter ALL TEMPLATES erhalten.")
    print("[OK] Entfernte Einträge bleiben nach Neustart entfernt.")
    print("[OK] Neue Auswahl kann den Eintrag erneut hinzufügen.")
    print("[OK] Syntaxprüfung erfolgreich.")
    if changes:
        print("[GEAENDERT] " + ", ".join(changes))
    print("[FERTIG] VADAFOK Studio 2.23.2 Manage Recent Templates angewendet.")


def main():
    try:
        apply(Path(__file__).resolve().parent.parent)
    except Exception as exc:
        print(f"[FEHLER] {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
