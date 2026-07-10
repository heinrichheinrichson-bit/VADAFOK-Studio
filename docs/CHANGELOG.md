# CHANGELOG

## v2.14.1.1 - WAIT Runtime + Local Action Refresh

### Fixed
- ADD ACTION no longer rebuilds the entire Silent Director page.
- UPDATE ACTION no longer rebuilds the entire page.
- MOVE UP / MOVE DOWN refresh only the action list.
- DELETE refreshes only the action list.

### Added
- WAIT is now executed during RUN PRESET.
- WAIT status changes to WAITING.
- Remaining time is displayed live.
- Director Log records WAIT start and finish.
- STOP interrupts an active WAIT.

### Preserved
- F8.
- RUN PRESET.
- Banner + Text.
- OBS Workflow no-flicker fix.
- Live Card.
