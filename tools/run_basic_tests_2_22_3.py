"""Run the VADAFOK Studio basic foundation checks."""

from __future__ import annotations

import compileall
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_unit_tests() -> bool:
    suite = unittest.defaultTestLoader.discover(
        str(PROJECT_ROOT / "tests"),
        pattern="test_*.py",
        top_level_dir=str(PROJECT_ROOT),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


def compile_project() -> bool:
    return compileall.compile_dir(
        str(PROJECT_ROOT / "vadafok_studio"),
        quiet=1,
        force=True,
    )


def show_git_hygiene() -> None:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        print("\nGit status --short:")
        print(result.stdout.strip() or "(keine lokalen Änderungen)")
    except Exception as exc:
        print(f"Git-Status konnte nicht gelesen werden: {exc}")


def main() -> int:
    print("VADAFOK Studio 2.22.3 - Foundation - Basic Tests")
    print("=" * 58)

    unit_ok = run_unit_tests()
    compile_ok = compile_project()

    print()
    print("[OK]" if unit_ok else "[FEHLER]", "Unit-/Foundation-Tests")
    print("[OK]" if compile_ok else "[FEHLER]", "Compileall vadafok_studio")
    show_git_hygiene()

    if unit_ok and compile_ok:
        print("\n[FERTIG] Alle Basic Tests wurden bestanden.")
        return 0

    print("\n[FEHLER] Mindestens ein Basic Test ist fehlgeschlagen.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
