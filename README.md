# VADAFOK Studio 2.6.3

## Ziel

Undo / Redo im Template Editor.

## Neu

- `Ctrl + Z` = Undo
- `Ctrl + Y` = Redo
- Buttons:
  - `UNDO`
  - `REDO`

## Unterstützte Aktionen

Undo / Redo funktioniert für:

- Feld verschieben
- Feld skalieren
- Group Move
- Copy Field
- Multi Copy
- Delete Field
- Multi Delete
- Align
- Distribute
- Keyboard Move
- Property-Änderungen wie Name/Größe/Farbe

## Hinweise

- History ist pro Session aktiv.
- Beim Start des Studios ist die History leer.
- Die maximale History-Größe liegt aktuell bei 80 Zuständen.

## Test

1. Feld verschieben.
2. Ctrl + Z testen.
3. Ctrl + Y testen.
4. Feld skalieren.
5. Ctrl + Z / Ctrl + Y testen.
6. Copy Field testen.
7. Delete Field testen.
8. Multi Selection + Group Move testen.
9. Align testen.
10. Keyboard Move testen.
11. Card Creator kurz prüfen.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.6.3 - Add undo and redo to Template Editor"
git push
```

## Commit-Beschreibung

```text
v2.6.3 - Add undo and redo to Template Editor

- Added undo/redo history for Template Editor
- Ctrl+Z and Ctrl+Y shortcuts
- Added UNDO and REDO buttons
- Supports move, resize, group move, copy, delete, align, distribute and keyboard editing
- Maintains existing Smart Guides, Zoom, Pan, Multi Selection and Card Creator behavior
```
