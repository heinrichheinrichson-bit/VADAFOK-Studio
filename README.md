# VADAFOK Studio 2.5.7

## Ziel

Pan Anti-Flicker im Template Editor.

## Problem in 2.5.6

Pan funktionierte, aber beim Verschieben des gezoomten Bildes wurde das komplette Canvas neu gezeichnet.
Dadurch wurde das Hintergrundbild kurz ausgeblendet bzw. neu geladen.

## Repariert

Beim Pan wird jetzt nicht mehr neu gerendert.

Stattdessen:

```text
canvas.move("all", dx, dy)
```

Das bedeutet:

- Hintergrundbild bleibt sichtbar
- Feldrahmen bleiben sichtbar
- Handles bleiben sichtbar
- kein erneutes Laden der PNG
- kein Flackern beim Pan

## Verhalten

- Zoom ändern → zeichnet einmal neu
- Pan bewegen → verschiebt vorhandene Canvas-Objekte
- PAN RESET → zeichnet einmal neu
- 100% → setzt Zoom und Pan zurück

## Test

1. Template Editor öffnen.
2. Stark hineinzoomen.
3. Mittlere Maustaste ziehen.
4. Prüfen: Kein Wegflackern.
5. Shift + linke Maustaste ziehen.
6. Prüfen: Kein Wegflackern.
7. Nach dem Pan ein Feld anklicken.
8. Feld verschieben/skalieren.
9. COPY FIELD testen.
10. Card Creator kurz prüfen.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.5.7 - Smooth pan without canvas redraw"
git push
```

## Commit-Beschreibung

```text
v2.5.7 - Smooth pan without canvas redraw

- Pan now moves existing canvas items instead of redrawing
- Background no longer reloads during pan
- Removed pan flicker in Template Editor
- Keeps hit testing coordinates synchronized after pan
- Zoom, Copy Field and Card Creator remain unchanged
```
