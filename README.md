# VADAFOK Studio 2.6.2

## Ziel

Keyboard Editing im Template Editor.

## Neu

- Pfeiltasten bewegen ausgewählte Felder um 1 px
- Shift + Pfeiltaste bewegt ausgewählte Felder um 10 px
- Delete / Backspace löscht Auswahl
- Ctrl + D dupliziert Auswahl
- Ctrl + A wählt alle Felder
- Esc hebt Auswahl auf

## Funktioniert mit

- Einzelauswahl
- Multi Selection
- Group Move
- Multi Copy
- Smart Guides
- Zoom / Pan
- Alignment Tools

## Test

1. Ein Feld auswählen.
2. Pfeiltasten testen.
3. Shift + Pfeiltasten testen.
4. Mehrere Felder mit Ctrl + Klick auswählen.
5. Pfeiltasten testen: alle ausgewählten Felder müssen sich bewegen.
6. Ctrl + D testen.
7. Ctrl + A testen.
8. Delete / Backspace testen.
9. Esc testen.
10. Smart Guides / Align / Card Creator kurz prüfen.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.6.2 - Add keyboard editing to Template Editor"
git push
```

## Commit-Beschreibung

```text
v2.6.2 - Add keyboard editing to Template Editor

- Added arrow-key movement for selected template fields
- Shift+Arrow moves selected fields by 10 px
- Delete/Backspace deletes selected fields
- Ctrl+D duplicates selected fields
- Ctrl+A selects all fields
- Esc clears selection
- Works with multi-selection, group move, Smart Guides, Zoom, Pan and Alignment Tools
```
