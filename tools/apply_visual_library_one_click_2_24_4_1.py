"""Apply VADAFOK Studio 2.24.4.1 one-click visual Library picker."""

from __future__ import annotations

import py_compile
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path


AUTO_APPLY_BLOCK = (
    "\n"
    "        if getattr(\n"
    "            self,\n"
    "            \"library_template_background_picker_mode\",\n"
    "            False,\n"
    "        ):\n"
    "            selected = getattr(self, \"selected_item\", None)\n"
    "            if selected is not None and getattr(selected, \"kind\", \"\") == \"image\":\n"
    "                self.assign_selected_template_background()\n"
)


def find_method(source: str, method_name: str) -> re.Match[str]:
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
    return matches[0]


def add_auto_apply(source: str) -> tuple[str, bool]:
    method_match = find_method(source, "select_library_item")
    method = method_match.group(0)

    if (
        "library_template_background_picker_mode" in method
        and "self.assign_selected_template_background()" in method
    ):
        return source, False

    # Append the guarded picker-only behavior at the end of the existing
    # selection method. The normal Library path therefore remains unchanged.
    updated_method = method.rstrip() + AUTO_APPLY_BLOCK + "\n"

    return (
        source[:method_match.start()]
        + updated_method
        + source[method_match.end():],
        True,
    )


def validate(source: str) -> None:
    select_method = find_method(source, "select_library_item").group(0)
    assign_method = find_method(
        source,
        "assign_selected_template_background",
    ).group(0)

    required_select = (
        "library_template_background_picker_mode",
        'getattr(selected, "kind", "") == "image"',
        "self.assign_selected_template_background()",
    )
    missing = [
        value for value in required_select
        if value not in select_method
    ]
    if missing:
        raise RuntimeError(
            "One-Click-Validierung fehlgeschlagen: " + ", ".join(missing)
        )

    if "self.show_template_editor_page()" not in assign_method:
        raise RuntimeError(
            "Die Hintergrundübernahme kehrt nicht zum Template Editor zurück."
        )


def apply(project_root: Path) -> None:
    app_path = project_root / "vadafok_studio" / "app.py"
    backup_path = app_path.with_suffix(".py.before_2_24_4_1.bak")

    if not app_path.is_file():
        raise RuntimeError(f"app.py fehlt: {app_path}")

    original = app_path.read_text(encoding="utf-8")
    updated, changed = add_auto_apply(original)
    validate(updated)

    shutil.copy2(app_path, backup_path)
    app_path.write_text(updated, encoding="utf-8")
    print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        for path in (
            app_path,
            project_root / "vadafok_studio" / "version.py",
            project_root / "tests" / "test_version.py",
            project_root / "tests" / "test_template_background_one_click.py",
        ):
            py_compile.compile(str(path), doraise=True)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_template_background_one_click",
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
                "Automatische One-Click-Tests fehlgeschlagen "
                f"(Exit-Code {result.returncode})."
            )
    except Exception:
        shutil.copy2(backup_path, app_path)
        print("[ROLLBACK] app.py wurde automatisch wiederhergestellt.")
        raise

    print("[OK] Bildklick übernimmt im Picker-Modus sofort den Hintergrund.")
    print("[OK] Automatische Rückkehr zum Template Editor bleibt aktiv.")
    print("[OK] SHOW / USE ist im Picker-Modus nicht mehr erforderlich.")
    print("[OK] Normaler Library-Betrieb bleibt unverändert.")
    print("[OK] Python-Syntaxprüfung erfolgreich.")
    if changed:
        print("[GEAENDERT] One-Click-Übernahme in select_library_item.")
    print(
        "[FERTIG] VADAFOK Studio 2.24.4.1 "
        "Visual Library One-Click Apply angewendet."
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
