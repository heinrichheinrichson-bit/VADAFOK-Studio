# VADAFOK Studio 2.6.1

## Ziel

Alignment Tools für Multi Selection im Template Editor.

## Neu

Wenn mehrere Felder ausgewählt sind:

- `ALIGN LEFT`
- `CENTER`
- `ALIGN RIGHT`
- `ALIGN TOP`
- `MIDDLE`
- `ALIGN BOTTOM`
- `DISTRIBUTE H`
- `DISTRIBUTE V`

## Verhalten

### Align

Richtet alle ausgewählten Felder an der gemeinsamen Auswahlbox aus.

### Distribute

Verteilt mindestens drei ausgewählte Felder gleichmäßig:

- horizontal nach X-Position
- vertikal nach Y-Position

## Test

1. Mit Ctrl + Klick mehrere Felder auswählen.
2. `ALIGN LEFT` testen.
3. `CENTER` testen.
4. `ALIGN RIGHT` testen.
5. `ALIGN TOP`, `MIDDLE`, `ALIGN BOTTOM` testen.
6. Drei oder mehr Felder auswählen.
7. `DISTRIBUTE H` und `DISTRIBUTE V` testen.
8. Group Move, Multi-Copy, Smart Guides, Zoom/Pan kurz prüfen.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.6.1 - Add alignment tools for multi selection"
git push
```

## Commit-Beschreibung

```text
v2.6.1 - Add alignment tools for multi selection

- Added alignment buttons for selected template fields
- Supports left, center, right, top, middle and bottom alignment
- Added horizontal and vertical distribution for 3+ fields
- Works with existing multi-selection and group move
- Existing Smart Guides, Zoom, Pan and Copy Field behavior preserved
```
