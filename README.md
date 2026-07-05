# VADAFOK Studio 2.5.4

## Ziel

Komfortfunktion im Template Editor:

```text
COPY FIELD
```

## Neu

Neben `DELETE FIELD` gibt es jetzt `COPY FIELD`.

## Verhalten

1. Feld auswählen.
2. `COPY FIELD` drücken.
3. Das Feld wird komplett dupliziert.

Die Kopie übernimmt:

- Position, leicht versetzt
- Breite
- Höhe
- Schrift
- Schriftgröße
- Textfarbe
- Outline-Farbe
- Outline-Stärke
- Uppercase
- alle gespeicherten Feldeigenschaften

Der Name wird automatisch eindeutig:

```text
game
game_copy
game_copy2
game_copy3
```

Nach dem Kopieren:

- die Kopie ist sofort ausgewählt
- das Name-Feld im Properties Panel wird fokussiert und markiert
- du kannst direkt einen neuen Namen tippen

## Test

1. Template Editor öffnen.
2. Feld auswählen.
3. `COPY FIELD`.
4. Prüfen:
   - neues Feld erscheint leicht versetzt
   - Größe und Styling identisch
   - Kopie ist ausgewählt
   - Name kann direkt geändert werden
5. Speichern.
6. Studio neu starten.
7. Prüfen: kopiertes Feld bleibt vorhanden.
8. Card Creator öffnen.
9. Prüfen: neues Eingabefeld erscheint.

## Git

Wenn alles passt:

```bash
git add .
git commit -m "v2.5.4 - Add Copy Field to Template Editor"
git push
```
