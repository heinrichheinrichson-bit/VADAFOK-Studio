from __future__ import annotations

import compileall
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("VADAFOK Studio 2.22.4 - Foundation - Warning Cleanup")
    print("=" * 58)

    suite = unittest.defaultTestLoader.discover(
        str(PROJECT_ROOT / "tests"),
        pattern="test_*.py",
        top_level_dir=str(PROJECT_ROOT),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    compile_ok = compileall.compile_dir(
        str(PROJECT_ROOT / "vadafok_studio"),
        quiet=1,
        force=True,
    )

    print()
    print("[OK]" if result.wasSuccessful() else "[FEHLER]", "Unit-/Foundation-Tests")
    print("[OK]" if compile_ok else "[FEHLER]", "Compileall vadafok_studio")

    if result.wasSuccessful() and compile_ok:
        print("[FERTIG] Alle 2.22.4-Tests wurden bestanden.")
        return 0

    print("[FEHLER] Mindestens ein Test ist fehlgeschlagen.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
