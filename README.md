# VADAFOK Studio 2.5.8

## Ziel

Smart Guides + Smart Snap im Template Editor.

## Neu

Im Template Editor gibt es jetzt:

- `SMART GUIDES`
- `SMART SNAP`

## SMART GUIDES

Beim Verschieben oder Skalieren eines Feldes erscheinen goldene Hilfslinien, wenn das Feld nahe an wichtigen Positionen ist:

- linke/rechte Kante anderer Felder
- horizontale/vertikale Mitte anderer Felder
- Template-Mitte
- Template-Kanten

## SMART SNAP

Wenn aktiviert, rastet das Feld automatisch an diese Hilfslinien ein.

## Bedienung

1. Feld anklicken.
2. Feld ziehen oder skalieren.
3. Goldene Hilfslinien erscheinen automatisch.
4. Bei aktivem `SMART SNAP` springt das Feld exakt auf die Linie.

## Weiterhin vorhanden

- Zoom
- Pan ohne Flackern
- COPY FIELD
- Card Creator
- Template-Verwaltung

## Test

1. Zwei Felder im Template haben.
2. `SMART GUIDES` aktiv lassen.
3. Ein Feld nahe an die Kante/Mitte des anderen Feldes ziehen.
4. Goldene Hilfslinie muss erscheinen.
5. `SMART SNAP` aktivieren.
6. Feld muss beim Ziehen leicht einrasten.
7. Template-Mitte testen.
8. Resize an Kanten testen.
9. Zoom + Pan testen.
10. COPY FIELD kurz prüfen.

## Installation

1. ZIP entpacken.
2. Den entpackten Ordner wie gewohnt starten.
3. Diese Version nicht über Git speichern, bevor die Tests bestanden sind.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.5.8 - Add Smart Guides and Smart Snap"
git push
```

## Commit-Beschreibung

```text
v2.5.8 - Add Smart Guides and Smart Snap

- Added smart guide lines in Template Editor
- Added smart snapping for field move and resize
- Supports snapping to template center, template edges and other fields
- Smart guides work with zoom and pan
- Existing zoom, pan, copy field and Card Creator behavior preserved
```
