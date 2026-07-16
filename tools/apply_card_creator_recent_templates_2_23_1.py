"""Apply VADAFOK Studio 2.23.1 recent templates."""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
from pathlib import Path

IMPORT_LINE = "from .core.recent_templates import load_recent_templates, record_recent_template"
INIT_LINE = "        self.card_recent_templates = load_recent_templates(list_templates())"
RECORD_LINE = "        self.card_recent_templates = record_recent_template(name, list_templates())"

RECENT_UI = (
    "        recent_names = load_recent_templates(names)\n"
    "        self.card_recent_templates = recent_names\n"
    "        if recent_names:\n"
    "            ctk.CTkLabel(\n"
    "                tlist,\n"
    "                text=\"RECENT TEMPLATES\",\n"
    "                text_color=GOLD,\n"
    "                anchor=\"w\",\n"
    "                font=ctk.CTkFont(size=12, weight=\"bold\"),\n"
    "            ).pack(fill=\"x\", padx=8, pady=(8, 3))\n"
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
    "            ctk.CTkLabel(\n"
    "                tlist,\n"
    "                text=\"ALL TEMPLATES\",\n"
    "                text_color=\"#BCA870\",\n"
    "                anchor=\"w\",\n"
    "                font=ctk.CTkFont(size=11, weight=\"bold\"),\n"
    "            ).pack(fill=\"x\", padx=8, pady=(12, 3))\n"
)


def insert_after_match(source, pattern, insertion, label):
    if insertion.strip() in source:
        return source, False
    match = re.search(pattern, source, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"{label} wurde nicht gefunden.")
    return source[:match.end()] + "\n" + insertion + source[match.end():], True


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    backup_path = app_path.with_suffix(".py.before_2_23_1.bak")
    original = app_path.read_text(encoding="utf-8")
    updated = original
    changes = []

    updated, changed = insert_after_match(
        updated,
        r"^from \.core\.template_store import .+$",
        IMPORT_LINE,
        "Template-Store-Import",
    )
    if changed:
        changes.append("Import")

    updated, changed = insert_after_match(
        updated,
        r'^\s*self\.card_selected_template\s*=\s*ctk\.StringVar\(value=""\)\s*$',
        INIT_LINE,
        "Card-Creator-Initialisierung",
    )
    if changed:
        changes.append("Initialisierung")

    if "recent_names = load_recent_templates(names)" not in updated:
        match = re.search(
            r'(^\s*tlist\.grid\(row=1,\s*column=0,\s*sticky="nsew",\s*padx=18,\s*pady=\(0,\s*18\)\)\s*$)',
            updated,
            flags=re.MULTILINE,
        )
        if not match:
            raise RuntimeError("Template-Liste im Card Creator wurde nicht gefunden.")
        updated = updated[:match.end()] + "\n" + RECENT_UI + updated[match.end():]
        changes.append("Oberfläche")

    if RECORD_LINE not in updated:
        match = re.search(
            r'(^\s*def card_select_template\(self,\s*name\):\s*$)',
            updated,
            flags=re.MULTILINE,
        )
        if not match:
            raise RuntimeError("card_select_template wurde nicht gefunden.")
        updated = updated[:match.end()] + "\n" + RECORD_LINE + updated[match.end():]
        changes.append("Aufzeichnung")

    for required in (IMPORT_LINE, INIT_LINE, "RECENT TEMPLATES", RECORD_LINE):
        if required not in updated:
            raise RuntimeError(f"Validierung fehlgeschlagen: {required}")

    if updated != original:
        shutil.copy2(app_path, backup_path)
        app_path.write_text(updated, encoding="utf-8")
        print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    gitignore = project_root / ".gitignore"
    text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    entry = "data/card_creator_recent_templates.json"
    if entry not in {line.strip() for line in text.splitlines()}:
        sep = "" if not text or text.endswith("\n") else "\n"
        gitignore.write_text(
            text + sep + "\n# User-specific Card Creator history\n" + entry + "\n",
            encoding="utf-8",
        )
    print("[OK] Benutzerbezogener Verlauf wird von Git ignoriert.")

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

    print("[OK] Verlauf dauerhaft gespeichert.")
    print("[OK] Maximal zehn Einträge und keine Duplikate.")
    print("[OK] Zuletzt verwendetes Template steht oben.")
    print("[OK] Syntaxprüfung erfolgreich.")
    print("[GEAENDERT] " + ", ".join(changes))
    print("[FERTIG] VADAFOK Studio 2.23.1 Recent Templates angewendet.")


def main():
    try:
        apply(Path(__file__).resolve().parent.parent)
    except Exception as exc:
        print(f"[FEHLER] {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
