# CHANGELOG

## v2.16.5.1 - Voice Trigger Rebuild + Icon Fix

### Fixed
- Added the missing global `Path` import.
- Rebuilt voice startup and status handling.
- Added explicit READY, WARNING, ERROR and HEARD messages.
- Added listener restart button.
- Added fallback when the selected speech culture is unavailable.
- Moved icon assets inside the Python package for reliable path resolution.
- Added Windows AppUserModelID for better taskbar icon behavior.

### Voice command
- `Live Card` opens the same Quick Caption window as F8.
- Local Windows System.Speech only.
- No microphone audio is sent to OBS.

<!-- VADAFOK-2.16.6-HYBRID-VOICE -->
## 2.16.6 – Hybrid Voice Quick Caption

- Added stable command recognition for opening, sending, clearing, and cancelling Quick Caption.
- Added local German and English dictation with faster-whisper.
- Added a separate Voice Library and fuzzy phrase matcher.
- Added read-only matching against existing Quick Card texts.
- Added centralized release version metadata and consistent visible version labels.
- Preserved the existing Quick Caption SHOW path for OBS output.

