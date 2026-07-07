# CHANGELOG

## v2.11.3.2 - True No-Flicker Source Toggle

### Fixed
- Source SHOW/HIDE no longer rebuilds the OBS Workflow page.
- Only the affected source row is updated.
- The visible flackering after Source SHOW/HIDE should be gone.

### Kept
- Source visibility changes are still sent to OBS immediately.
- Source status colors update directly.
- Workflow state/log still records the action internally.
