# VADAFOK Studio

VADAFOK Studio is a Windows desktop application for live-stream production with OBS. It combines scene control, overlay installation, Live Cards, Quick Cards, captions, templates, sound effects, speech control, Whisper dictation, and DeepL translation in one workflow-oriented interface.

## Current release

The application version is defined centrally in `vadafok_studio/version.py`. The title bar, sidebar, logs, launcher metadata, and release tests use this source of truth.

## Start on Windows

For normal use, start:

```text
VADAFOK Studio.exe
```

The launcher opens the current Python project without a visible command window. The legacy development starter remains available:

```text
Start VADAFOK Studio.bat
```

## Requirements

- Windows 10 or Windows 11
- Python 3.13 or newer
- OBS Studio with obs-websocket enabled
- Project dependencies from the included requirements files
- Optional: DeepL API key for translation
- Optional: faster-whisper model for local dictation

Install the main Python dependencies with:

```bash
py -m pip install -r requirements.txt
```

Some features have additional requirement files. Install only those needed by your setup.

## Launcher build

Run:

```text
BUILD_VADAFOK_STUDIO_EXE.bat
```

The script reads the version from `vadafok_studio/version.py`, generates Windows metadata, and creates `VADAFOK Studio.exe`. Temporary PyInstaller output is written below `launcher_build/` and is intentionally excluded from Git.

## OBS connection

1. Open OBS Studio.
2. Enable the obs-websocket server in OBS settings.
3. Enter the matching host, port, and password in **OBS Connection**.
4. Use **OBS Workflow** to scan scenes, inspect overlay health, and install missing sources.

## Core workflows

### Quick Caption / compact Live Card

Press **F8** or use the `Live Card` voice command to open the compact Quick Caption window. Whisper inserts the recognized German text into the existing textbox. An English preview appears in the same window. `VADAFOK ENGLISH` replaces the textbox content with the prepared English translation. `SHOW` sends the text and closes the compact window.

### Quick Cards

Quick Cards provide reusable prepared messages. Voice matching and translation can select German or English text before sending.

### Voice commands

Important commands include:

```text
Live Card
VADAFOK ENGLISH
SHOW
RESET
STOP
```

Command phrases and aliases are stored in `vadafok_studio/voice_control/voice_library.json`.

## Configuration and user data

Runtime configuration and user-specific data are stored below `data/`. Logs are stored below `logs/`. These files may contain machine-specific settings and should not be committed unless they are intentional defaults.

## Tests

Run the complete standard-library test suite with:

```bash
py -m unittest discover -s tests -v
```

Release tests must not contain hard-coded historical version numbers. They should validate the central version source or behavior instead.

## Project structure

```text
vadafok_studio/app.py              Main application shell and legacy UI composition
vadafok_studio/core/               OBS, rendering, templates, layout, and storage
vadafok_studio/services/           Application services
vadafok_studio/translator/         Translation providers and runtime
vadafok_studio/voice_control/      Voice commands, Whisper, and language workflows
launcher/                          Native Windows launcher source and metadata generator
tests/                             Automated regression and release tests
```

`app.py` is currently the largest maintenance area. Future architecture work should extract one tested view or workflow at a time without changing behavior during the move.

## Troubleshooting

- **Launcher build says “Permission denied”**: close VADAFOK Studio and wait a few seconds before rebuilding or committing. Windows Defender may briefly hold PyInstaller files.
- **OBS is disconnected**: confirm OBS is running and the websocket settings match.
- **Translation is unavailable**: verify the DeepL API key and network access.
- **Voice recognition does not start**: verify microphone access and the optional Whisper dependencies.

## Development policy

Prefer small, tested changes. Functional changes and architectural moves should be separate commits. After every extraction from `app.py`, run the complete test suite and manually verify the affected GUI workflow.
