# VADAFOK Studio 2.3.5

## Basis

Direkt aus der stabilen Nutzer-ZIP `Studio 2.2.1`.

## Ziel

Gezielter Fix für das Template-Editor-Flackern beim Klick und Ziehen.

## Diagnose

Das Bild flackerte bereits bei einfachem Klick ins Multi-Field-Layout.
Deshalb war nicht nur das Ziehen das Problem, sondern `template_mouse_down`.

## Änderung

- Klick ins leere Canvas zeichnet nichts mehr neu.
- Klick auf ein Feld aktualisiert nur die Feld-Overlays.
- Ziehen aktualisiert nur die Feld-Overlays.
- Der Hintergrund bleibt stehen.
- Alle Feld-Overlays bekommen den Canvas-Tag `template_overlay`.

## Nicht verändert

- Library
- SHOW / USE
- SET BACKGROUND FROM LIBRARY
- BACKGROUND AUS DATEI
- Card Creator
- Template-Ordnerstruktur

## Test

1. Library → Template-Bild auswählen → SHOW / USE.
2. Template Editor öffnen.
3. Ins schwarze freie Canvas klicken.
   - Bild darf nicht wegflackern.
4. Feld anklicken.
   - Bild darf nicht wegflackern.
5. Feld ziehen.
   - Bild soll stehen bleiben.
   - keine doppelten Felder.
6. Feldgröße ändern.
   - Bild soll stehen bleiben.
   - keine doppelten Felder.
7. Card Creator kurz prüfen.

## Git

Nur committen, wenn Klick + Ziehen stabil sind und Library/Background weiter funktionieren.
