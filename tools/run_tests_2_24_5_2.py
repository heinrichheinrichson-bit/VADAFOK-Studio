from __future__ import annotations
import compileall
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    print("VADAFOK Studio 2.24.5.2 - Library Picker Runtime Return Fix")
    print("=" * 70)
    suite = unittest.defaultTestLoader.discover(
        str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT)
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    compile_ok = compileall.compile_dir(
        str(ROOT / "vadafok_studio"), quiet=1, force=True
    )
    print()
    print("[OK]" if result.wasSuccessful() else "[FEHLER]", "Alle Tests")
    print("[OK]" if compile_ok else "[FEHLER]", "Compileall")
    if result.wasSuccessful() and compile_ok:
        print("[FERTIG] Alle 2.24.5.2-Tests wurden bestanden.")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
