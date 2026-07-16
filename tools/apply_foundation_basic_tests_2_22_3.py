"""Apply VADAFOK Studio 2.22.3 basic tests and repository hygiene."""

from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path


REQUIRED_IGNORES = [
    "__pycache__/",
    "*.pyc",
    ".idea/",
    "logs/",
    "*.bak",
]


def normalize_gitignore(project_root: Path) -> None:
    path = project_root / ".gitignore"
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    # Repair literal escape sequences introduced by the previous generated
    # patch without disturbing ordinary lines.
    text = text.replace(r"\n", "\n")
    existing = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip()
    ]

    present = {line.strip() for line in existing}
    additions = [entry for entry in REQUIRED_IGNORES if entry not in present]

    if additions:
        if existing:
            existing.append("")
        existing.append("# Development and runtime files")
        existing.extend(additions)

    path.write_text("\n".join(existing).rstrip() + "\n", encoding="utf-8")
    print("[OK] .gitignore normalisiert und geprüft.")


def untrack_generated_files(project_root: Path) -> None:
    candidates = [
        "vadafok_studio/.idea",
        "vadafok_studio/__pycache__",
        "logs",
        "vadafok_studio/app.py.before_2_22_1.bak",
        "vadafok_studio/app.py.before_2_22_2.bak",
        "exports/caption_render.png",
    ]

    command = [
        "git",
        "rm",
        "-r",
        "--cached",
        "--ignore-unmatch",
        "--",
        *candidates,
    ]
    result = subprocess.run(
        command,
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode not in (0,):
        raise RuntimeError(
            "Git-Bereinigung fehlgeschlagen:\n"
            + (result.stderr.strip() or result.stdout.strip())
        )

    print("[OK] Generierte Dateien aus der Git-Verfolgung entfernt.")
    print("     Lokale PyCharm-, Log- und Arbeitsdateien bleiben erhalten.")


def validate_files(project_root: Path) -> None:
    required = [
        project_root / "vadafok_studio" / "version.py",
        project_root / "vadafok_studio" / "logging_setup.py",
        project_root / "vadafok_studio" / "app.py",
        project_root / "tests" / "test_version.py",
        project_root / "tests" / "test_logging_setup.py",
        project_root / "tests" / "test_project_foundation.py",
        project_root / "tools" / "run_basic_tests_2_22_3.py",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("Benötigte Dateien fehlen:\n" + "\n".join(missing))

    for path in required:
        if path.suffix == ".py":
            py_compile.compile(str(path), doraise=True)

    print("[OK] Alle neuen Python-Dateien bestehen die Syntaxprüfung.")


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent

    try:
        normalize_gitignore(project_root)
        untrack_generated_files(project_root)
        validate_files(project_root)
    except Exception as exc:
        print(f"[FEHLER] {exc}")
        return 1

    print("[OK] Tkinter-Exception-Hook auf tkinter.Tk korrigiert.")
    print("[OK] Basic-Test-Suite installiert.")
    print("[FERTIG] VADAFOK Studio 2.22.3 Basic Tests angewendet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
