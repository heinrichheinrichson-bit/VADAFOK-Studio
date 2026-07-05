# VADAFOK Studio 2.6.5

## Ziel

Lock / Unlock Fields im Template Editor.

## Neu

Im `LAYERS` Panel gibt es jetzt pro Feld einen Lock-Button:

- `○` = nicht gesperrt
- `🔒` = gesperrt

## Verhalten gesperrter Felder

Gesperrte Felder:

- können sichtbar bleiben
- werden weiterhin gerendert
- können im Layer Panel ausgewählt werden
- können nicht versehentlich verschoben werden
- können nicht versehentlich skaliert werden
- werden bei Multi-Delete übersprungen
- werden bei Group Move nicht mitbewegt
- werden bei Keyboard Move nicht bewegt
- werden bei Align / Distribute nicht bewegt

## Weiterhin vorhanden

- Layer Panel
- Undo / Redo
- Keyboard Editing
- Multi Selection
- Group Move
- Multi Copy / Delete
- Alignment Tools
- Smart Guides
- Zoom / Pan
- Card Creator

## Test

1. Template Editor öffnen.
2. Im Layer Panel ein Feld mit `○` sperren.
3. Prüfen: Button zeigt `🔒`.
4. Gesperrtes Feld im Canvas ziehen.
5. Prüfen: Es bewegt sich nicht.
6. Mehrere Felder auswählen, eins davon gesperrt.
7. Group Move testen: nur ungesperrte Felder bewegen sich.
8. Delete bei Auswahl mit gesperrtem Feld testen.
9. Align / Distribute mit gesperrtem Feld testen.
10. Undo / Redo für Lock testen.
11. Speichern und neu starten: Lock-Status bleibt erhalten.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.6.5 - Add lock and unlock fields"
git push
```

## Commit-Beschreibung

```text
v2.6.5 - Add lock and unlock fields

- Added lock toggle per field in the Layers panel
- Locked fields cannot be moved or resized
- Locked fields are skipped by group move, keyboard move, align and distribute
- Multi-delete skips locked fields
- Lock state is saved with templates
- Existing Layer Panel, Undo/Redo, Smart Guides, Zoom, Pan and Card Creator behavior preserved
```
