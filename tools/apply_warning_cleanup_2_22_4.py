"""Apply VADAFOK Studio 2.22.4 warning cleanup."""

from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

OLD_BLOCK = (
    "    finally:\n"
    "        if getattr(self, \"voice_stop_requested\", False) or saw_error:\n"
    "            return\n"
    "\n"
    "        try:\n"
    "            exit_code = process.poll()\n"
    "        except Exception:\n"
    "            exit_code = None\n"
    "\n"
    "        detail = f\" · exit {exit_code}\" if exit_code is not None else \"\"\n"
    "        self.after(0, lambda: _set_status(self, f\"STOPPED{detail}\"))\n"
)

NEW_BLOCK = (
    "    finally:\n"
    "        should_report_stopped = not (\n"
    "            getattr(self, \"voice_stop_requested\", False) or saw_error\n"
    "        )\n"
    "\n"
    "        if should_report_stopped:\n"
    "            try:\n"
    "                exit_code = process.poll()\n"
    "            except Exception:\n"
    "                exit_code = None\n"
    "\n"
    "            detail = f\" · exit {exit_code}\" if exit_code is not None else \"\"\n"
    "            self.after(0, lambda: _set_status(self, f\"STOPPED{detail}\"))\n"
)


def apply(project_root: Path) -> None:
    foundation_path = project_root / "vadafok_studio" / "voice_control" / "foundation.py"
    version_path = project_root / "vadafok_studio" / "version.py"
    test_path = project_root / "tests" / "test_voice_foundation_warnings.py"
    backup_path = foundation_path.with_suffix(".py.before_2_22_4.bak")

    for path in (foundation_path, version_path, test_path):
        if not path.is_file():
            raise RuntimeError(f"Benötigte Datei fehlt: {path}")

    original = foundation_path.read_text(encoding="utf-8")

    if NEW_BLOCK in original:
        print("[OK] Warning Cleanup war bereits angewendet.")
    else:
        count = original.count(OLD_BLOCK)
        if count != 1:
            raise RuntimeError(
                f"Erwartet wurde genau ein passender finally-Block, gefunden wurden {count}."
            )
        shutil.copy2(foundation_path, backup_path)
        foundation_path.write_text(original.replace(OLD_BLOCK, NEW_BLOCK, 1), encoding="utf-8")
        print(f"[OK] Sicherheitskopie erstellt: {backup_path.name}")

    try:
        py_compile.compile(str(foundation_path), doraise=True)
        py_compile.compile(str(version_path), doraise=True)
        py_compile.compile(str(test_path), doraise=True)
        result = subprocess.run(
            [
                sys.executable,
                "-W",
                "error::SyntaxWarning",
                "-m",
                "py_compile",
                str(foundation_path),
            ],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)
    except Exception:
        if backup_path.exists():
            shutil.copy2(backup_path, foundation_path)
        raise RuntimeError(
            "Prüfung fehlgeschlagen. foundation.py wurde automatisch wiederhergestellt."
        )

    print("[OK] Return aus finally-Block entfernt.")
    print("[OK] SyntaxWarning-Prüfung erfolgreich.")
    print("[OK] Regressionstest installiert.")
    print("[FERTIG] VADAFOK Studio 2.22.4 Warning Cleanup angewendet.")


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
