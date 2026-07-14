from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- VADAFOK-2.16.6-HYBRID-VOICE -->"

ROADMAP_SECTION = f"""\n\n{MARKER}\n## 2.16.6 – Hybrid Voice Quick Caption\n\nStatus: implemented and release-tested.\n\n- Windows Speech recognizes fixed commands: `Live Card`, `Vadafok Show`, `Vadafok Reset`, `Vadafok Stop`.\n- Local faster-whisper dictation supports German and English captions.\n- Voice Matcher compares recognized text with the separate Voice Library and existing Quick Cards without modifying Quick Cards.\n- Captions remain editable before they are sent through the existing SHOW/OBS path.\n- Future work: direct Quick Card selection, configurable command phrases, optional user learning, and broader voice settings.\n"""

IDEAS_SECTION = f"""\n\n{MARKER}\n## Voice control / silent-stream input\n\n- Use speech privately as a local input method while the public stream remains silent.\n- Trigger prepared Quick Cards by voice in a future release.\n- Add user-editable Voice Library phrases and common recognition aliases.\n- Consider optional learning from manually corrected transcriptions.\n- Keep Quick Cards focused on complete, frequently used comments and responses.\n"""

CHANGELOG_SECTION = f"""\n\n{MARKER}\n## 2.16.6 – Hybrid Voice Quick Caption\n\n- Added stable command recognition for opening, sending, clearing, and cancelling Quick Caption.\n- Added local German and English dictation with faster-whisper.\n- Added a separate Voice Library and fuzzy phrase matcher.\n- Added read-only matching against existing Quick Card texts.\n- Added centralized release version metadata and consistent visible version labels.\n- Preserved the existing Quick Caption SHOW path for OBS output.\n"""


def append_once(path: Path, section: str) -> str:
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = ""
    if MARKER in text:
        return f"unchanged: {path.name}"
    path.write_text(text.rstrip() + section + "\n", encoding="utf-8")
    return f"updated: {path.name}"


def main() -> None:
    results = [append_once(ROOT / "ROADMAP.md", ROADMAP_SECTION)]

    idea_candidates = [ROOT / "IDEAS.md", ROOT / "Ideas.md", ROOT / "docs" / "IDEAS.md"]
    ideas_path = next((p for p in idea_candidates if p.exists()), ROOT / "docs" / "IDEAS.md")
    ideas_path.parent.mkdir(parents=True, exist_ok=True)
    results.append(append_once(ideas_path, IDEAS_SECTION))

    changelog_candidates = [ROOT / "CHANGELOG.md", ROOT / "docs" / "CHANGELOG.md"]
    changelog_path = next((p for p in changelog_candidates if p.exists()), ROOT / "docs" / "CHANGELOG.md")
    changelog_path.parent.mkdir(parents=True, exist_ok=True)
    results.append(append_once(changelog_path, CHANGELOG_SECTION))

    obsolete = [
        "INSTALLIEREN_UND_TESTEN.txt",
        *[f"INSTALLIEREN_UND_TESTEN_TEST{i:02d}.txt" for i in range(2, 9)],
        "INSTALLIEREN_UND_TESTEN_TEST04A.txt",
        "INSTALL_WHISPER_TEST08.bat",
        "requirements_voice_test08.txt",
    ]
    for name in obsolete:
        path = ROOT / name
        if path.exists():
            path.unlink()
            results.append(f"removed: {name}")

    docs = ROOT / "docs"
    if docs.exists():
        for path in docs.glob("VOICE_CONTROL_TEST*_APPEND.md"):
            path.unlink()
            results.append(f"removed: docs/{path.name}")

    print("VADAFOK Studio 2.16.6 finalization complete:")
    for result in results:
        print(" -", result)


if __name__ == "__main__":
    main()
