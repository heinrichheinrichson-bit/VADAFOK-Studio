"""Apply VADAFOK Studio 2.23.3 partial recent refresh."""

from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
from pathlib import Path


OLD_REMOVE_METHOD = (
    "    def card_remove_recent_template(self, name):\n"
    "        self.card_recent_templates = remove_recent_template(\n"
    "            name, list_templates()\n"
    "        )\n"
    "        self.show_card_creator_page()\n"
    "\n"
)

NEW_METHODS = (
    "    def card_refresh_recent_templates(self):\n"
    "        frame = getattr(self, \"card_recent_templates_frame\", None)\n"
    "        if frame is None:\n"
    "            return\n"
    "\n"
    "        try:\n"
    "            if not frame.winfo_exists():\n"
    "                return\n"
    "        except Exception:\n"
    "            return\n"
    "\n"
    "        for child in self.card_recent_templates_frame.winfo_children():\n"
    "            child.destroy()\n"
    "\n"
    "        recent_names = load_recent_templates(list_templates())\n"
    "        self.card_recent_templates = recent_names\n"
    "\n"
    "        if not recent_names:\n"
    "            self.card_recent_templates_frame.pack_forget()\n"
    "            return\n"
    "\n"
    "        self.card_recent_templates_frame.pack(\n"
    "            fill=\"x\", padx=0, pady=0, before=self.card_all_templates_label\n"
    "        )\n"
    "\n"
    "        ctk.CTkLabel(\n"
    "            self.card_recent_templates_frame,\n"
    "            text=\"RECENT TEMPLATES\",\n"
    "            text_color=GOLD,\n"
    "            anchor=\"w\",\n"
    "            font=ctk.CTkFont(size=12, weight=\"bold\"),\n"
    "        ).pack(fill=\"x\", padx=8, pady=(8, 3))\n"
    "\n"
    "        for recent_name in recent_names:\n"
    "            recent_row = ctk.CTkFrame(\n"
    "                self.card_recent_templates_frame,\n"
    "                fg_color=\"transparent\",\n"
    "            )\n"
    "            recent_row.pack(fill=\"x\", padx=8, pady=3)\n"
    "            recent_row.grid_columnconfigure(0, weight=1)\n"
    "\n"
    "            prefix = (\n"
    "                \"✓ \"\n"
    "                if recent_name == self.card_selected_template.get()\n"
    "                else \"↶ \"\n"
    "            )\n"
    "            ctk.CTkButton(\n"
    "                recent_row,\n"
    "                text=prefix + recent_name,\n"
    "                anchor=\"w\",\n"
    "                fg_color=\"#3A2A0D\",\n"
    "                hover_color=\"#5A4318\",\n"
    "                command=lambda n=recent_name: self.card_select_template(n),\n"
    "            ).grid(row=0, column=0, sticky=\"ew\", padx=(0, 4))\n"
    "\n"
    "            ctk.CTkButton(\n"
    "                recent_row,\n"
    "                text=\"✕\",\n"
    "                width=28,\n"
    "                fg_color=\"#5A2424\",\n"
    "                hover_color=\"#7A3030\",\n"
    "                command=lambda n=recent_name: self.card_remove_recent_template(n),\n"
    "            ).grid(row=0, column=1)\n"
    "\n"
    "    def card_remove_recent_template(self, name):\n"
    "        self.card_recent_templates = remove_recent_template(\n"
    "            name, list_templates()\n"
    "        )\n"
    "        self.card_refresh_recent_templates()\n"
    "\n"
)

OLD_INLINE_BLOCK_START = "        recent_names = load_recent_templates(names)\n"
OLD_INLINE_BLOCK_END = (
    "            ).pack(fill=\"x\", padx=8, pady=(12, 3))\n"
)

NEW_CONTAINER_BLOCK = (
    "        self.card_recent_templates_frame = ctk.CTkFrame(\n"
    "            tlist,\n"
    "            fg_color=\"transparent\",\n"
    "        )\n"
    "\n"
    "        self.card_all_templates_label = ctk.CTkLabel(\n"
    "            tlist,\n"
    "            text=\"ALL TEMPLATES\",\n"
    "            text_color=\"#BCA870\",\n"
    "            anchor=\"w\",\n"
    "            font=ctk.CTkFont(size=11, weight=\"bold\"),\n"
    "        )\n"
    "        self.card_all_templates_label.pack(\n"
    "            fill=\"x\", padx=8, pady=(8, 3)\n"
    "        )\n"
    "\n"
    "        self.card_refresh_recent_templates()\n"
)


def replace_inline_recent_ui(source: str) -> tuple[str, bool]:
    if "self.card_recent_templates_frame = ctk.CTkFrame" in source:
        return source, False

    start = source.find(OLD_INLINE_BLOCK_START)
    if start < 0:
        raise RuntimeError("Beginn des bisherigen Recent-UI-Blocks wurde nicht gefunden.")

    end = source.find(OLD_INLINE_BLOCK_END, start)
    if end < 0:
        raise RuntimeError("Ende des bisherigen Recent-UI-Blocks wurde nicht gefunden.")

    end += len(OLD_INLINE_BLOCK_END)
    return source[:start] + NEW_CONTAINER_BLOCK + source[end:], True


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    backup_path = app_path.with_suffix(".py.before_2_23_3.bak")

    if not app_path.is_file():
        raise RuntimeError(f"app.py fehlt: {app_path}")

    original = app_path.read_text(encoding="utf-8")
    updated = original
    changes = []

    if NEW_METHODS not in updated:
        if OLD_REMOVE_METHOD not in updated:
            raise RuntimeError(
                "Die 2.23.2-Remove-Methode wurde nicht exakt gefunden."
            )
        updated = updated.replace(OLD_REMOVE_METHOD, NEW_METHODS, 1)
        changes.append("Partial-Refresh-Methode")

    updated, changed = replace_inline_recent_ui(updated)
    if changed:
        changes.append("Dedizierter Recent-Container")

    required = (
        "def card_refresh_recent_templates(self):",
        "self.card_refresh_recent_templates()",
        "self.card_recent_templates_frame = ctk.CTkFrame",
        "self.card_all_templates_label = ctk.CTkLabel",
    )
    missing = [value for value in required if value not in updated]
    if missing:
        raise RuntimeError(
            "Validierung fehlgeschlagen: " + ", ".join(missing)
        )

    remove_start = updated.index("def card_remove_recent_template")
    select_start = updated.index("def card_select_template", remove_start)
    remove_method = updated[remove_start:select_start]
    if "show_card_creator_page" in remove_method:
        raise RuntimeError(
            "Die Remove-Methode lädt weiterhin die komplette Seite neu."
        )

    shutil.copy2(app_path, backup_path)
    app_path.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        paths = [
            app_path,
            project_root / "vadafok_studio" / "version.py",
            project_root / "tests" / "test_version.py",
            project_root / "tests" / "test_partial_recent_refresh.py",
        ]
        for path in paths:
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_partial_recent_refresh",
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

    print("[OK] Entfernen lädt nicht mehr die komplette Card-Creator-Seite.")
    print("[OK] Nur der Recent-Bereich wird neu aufgebaut.")
    print("[OK] Vorschau und Eingabefelder bleiben erhalten.")
    print("[OK] Leerer Recent-Bereich verschwindet ohne Seiten-Refresh.")
    print("[OK] Python-Syntaxprüfung erfolgreich.")
    if changes:
        print("[GEAENDERT] " + ", ".join(changes))
    print("[FERTIG] VADAFOK Studio 2.23.3 Partial Recent Refresh angewendet.")


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
