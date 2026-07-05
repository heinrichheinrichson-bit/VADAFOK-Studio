# VADAFOK Studio 2.5.3

## Ziel

Fix für Card-Creator-Template-Auswahl.

## Ursache

Der Card Creator hat intern noch die alte Legacy-Liste `template_profiles.json` verwendet.
Dadurch wurde die Auswahl nach einem Klick sofort wieder auf `Default Stream Plan` zurückgesetzt.

Beobachtet im Debug:

```text
Clicked Template: Test
card_selected_template: Default Stream Plan
```

## Repariert

- Card Creator nutzt jetzt nur noch die neue Template-Ordnerstruktur.
- Template-Klick setzt `card_selected_template` korrekt.
- `card_template()` lädt das wirklich ausgewählte Template.
- Kein Rückfall auf `Default Stream Plan`, solange die Auswahl gültig ist.
- Background-Suche bleibt robust.
- Hochformat-Templates werden mit echter Background-Größe gerendert.

## Test

1. Card Creator öffnen.
2. Template `Test` anklicken.
3. Prüfen: Button-Haken wechselt auf `Test`.
4. Preview zeigt das Bild von `Test`.
5. anderes Template anklicken.
6. Preview muss wechseln.
7. zwei Templates rendern und Export-PNGs prüfen.
8. Template Editor kurz prüfen:
   - Löschen bleibt bestehen
   - Umbenennen funktioniert
   - Duplizieren funktioniert
   - Felder ziehen flackerfrei

## Git

Erst committen, wenn Card Creator beim Template-Wechsel korrekt lädt.
