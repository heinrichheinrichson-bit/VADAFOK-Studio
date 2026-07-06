# VADAFOK Studio 2.8.1.1

## Fix

Style Presets:
- fehlender `style_engine` Import repariert
- Save Style sollte jetzt eine JSON-Datei in `styles/` schreiben
- vorhandene Styles werden vor dem Überschreiben abgefragt

Card Creator:
- `UNDO DATA`
- `REDO DATA`
- `CLEAR FIELDS` undo bleibt erhalten

## Installation

Direkt über v2.8.1 installieren:

1. VADAFOK Studio schließen.
2. ZIP entpacken.
3. Inhalt in Projektordner kopieren und überschreiben.
4. Mit `Start VADAFOK Studio.bat` starten.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.8.1.1 - Fix Style Engine import"
git push
```
