# CHANGELOG

## v2.6.5 - Add lock and unlock fields

### Added
- Lock / Unlock Button pro Feld im Layer Panel.
- Gesperrte Felder werden im Layer Panel mit `🔒` angezeigt.
- Lock-Zustand wird im Template gespeichert.

### Changed
- Group Move überspringt gesperrte Felder.
- Keyboard Move überspringt gesperrte Felder.
- Align und Distribute bewegen gesperrte Felder nicht.
- Delete überspringt gesperrte Felder.
- Undo / Redo unterstützt Lock / Unlock.

### Verified
- Feld sperren / entsperren funktioniert.
- Gesperrtes Feld kann nicht gezogen werden.
- Multi-Auswahl mit gesperrtem Feld funktioniert.
- Delete / Align / Keyboard Move respektieren Lock.
- Undo / Redo macht Lock-Zustand rückgängig bzw. wieder aktiv.
- Lock-Zustand bleibt nach Neustart erhalten.

## v2.6.4.1 - Add visible Layer Panel to Template Editor

### Added
- Sichtbares Layer Panel zwischen Canvas und Properties.
- Layer-Auswahl synchron mit Canvas-Auswahl.
- Layer-Reihenfolge über ▲ / ▼ steuerbar.

## v2.6.3 - Add undo and redo to Template Editor

### Added
- Ctrl + Z / Ctrl + Y
- UNDO / REDO Buttons
- History für Move, Resize, Copy, Delete, Align, Keyboard Move und weitere Editor-Aktionen.

## v2.6.2 - Add keyboard editing to Template Editor

### Added
- Pfeiltasten bewegen Felder.
- Shift + Pfeiltasten bewegen 10 px.
- Ctrl + A, Ctrl + D, Delete, Esc.

## v2.6.1 - Add alignment tools for multi selection

### Added
- Align Left / Center / Right
- Align Top / Middle / Bottom
- Distribute H / V

## v2.6.0.1 - Fix group drag selection handling

### Fixed
- Gruppenverschieben nach Multi Selection funktioniert korrekt.
