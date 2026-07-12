# Voice Control

## v2.16.5

First supported command:

- `Live Card`

Effect:

- Opens the same Quick Caption window as keyboard shortcut F8.

Implementation:

- Optional.
- Local Windows `System.Speech` recognition.
- Runs through a hidden PowerShell listener.
- No cloud API.
- No microphone audio is routed to OBS.

Settings:

- Enable/disable Voice Trigger.
- Configure command phrase.
- Optional recognition culture such as `de-DE` or `en-US`.
- Status and last recognized phrase are visible.

Future possibilities:

- named Quick Cards
- Silent Director preset triggers
- scene switching
- show/hide commands

Future commands must be added one at a time and require explicit user control.
