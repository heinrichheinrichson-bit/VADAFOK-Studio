# VADAFOK Studio 2.6.4.1

## Ziel

Layer Panel im Template Editor – sichtbarer, sauberer 4-Spalten-Aufbau.

## Fix gegenüber 2.6.4

In 2.6.4 wurde die Layer-Logik eingefügt, aber das Panel war im UI nicht sichtbar.
Diese Version baut den Template Editor bewusst als 4-Spalten-Layout auf:

```text
Templates | Canvas | Layers | Properties
```

## Neu

- Sichtbares `LAYERS` Panel zwischen Canvas und Properties
- Klick auf Layer wählt das passende Feld aus
- Canvas-Auswahl markiert den passenden Layer
- `▲` bewegt ein Feld nach vorne
- `▼` bewegt ein Feld nach hinten
- Layer-Reihenfolge wird im Template gespeichert
- Undo/Redo für Layer-Reihenfolge

## Weiterhin vorhanden

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
2. Prüfen: `LAYERS` Panel ist zwischen Canvas und Properties sichtbar.
3. Layer anklicken.
4. Prüfen: Feld wird im Canvas ausgewählt.
5. Feld im Canvas anklicken.
6. Prüfen: Layer wird markiert.
7. `▲` und `▼` testen.
8. Undo / Redo für Layer-Reihenfolge testen.
9. Speichern und neu starten.
10. Prüfen: Layer-Reihenfolge bleibt erhalten.
11. Smart Guides / Keyboard / Group Move kurz prüfen.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.6.4.1 - Add visible Layer Panel to Template Editor"
git push
```

## Commit-Beschreibung

```text
v2.6.4.1 - Add visible Layer Panel to Template Editor

- Reworked Template Editor into a 4-column layout
- Added visible Layers panel between canvas and properties
- Layer list selects matching template fields
- Canvas selection syncs back to layer list
- Added layer forward/back controls
- Layer order persists in templates and supports undo/redo
```
