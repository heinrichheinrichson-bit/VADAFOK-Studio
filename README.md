# VADAFOK Studio 2.6.0.1

## Ziel

Fix für Group Move.

## Problem in 2.6.0

Mehrfachauswahl funktionierte, aber beim Ziehen bewegte sich nur ein Feld.

Ursache:

Beim Klick auf ein bereits ausgewähltes Feld wurde die Auswahl wieder auf genau dieses eine Feld reduziert.

## Repariert

Wenn mehrere Felder ausgewählt sind und du auf eines davon klickst:

- Auswahl bleibt erhalten
- Drag bewegt die ganze Gruppe

Wenn du auf ein nicht ausgewähltes Feld klickst:

- Auswahl wird wie gewohnt auf dieses Feld reduziert

Ctrl + Klick bleibt:

- hinzufügen
- abwählen

## Test

1. Template Editor öffnen.
2. Mit Ctrl + Klick mehrere Felder auswählen.
3. Ohne Ctrl auf eines der ausgewählten Felder klicken und ziehen.
4. Prüfen: alle ausgewählten Felder bewegen sich gemeinsam.
5. Auf ein nicht ausgewähltes Feld klicken.
6. Prüfen: Auswahl reduziert sich auf dieses Feld.
7. Multi-Copy testen.
8. Multi-Delete testen.
9. Smart Guides / Zoom / Pan kurz prüfen.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.6.0.1 - Fix group drag selection handling"
git push
```

## Commit-Beschreibung

```text
v2.6.0.1 - Fix group drag selection handling

- Fixed group drag after multi-select
- Clicking an already selected field keeps the group selection
- Dragging a selected field now moves the whole selected group
- Clicking an unselected field still switches to single selection
- Multi-copy, multi-delete, Smart Guides, Zoom and Pan preserved
```
