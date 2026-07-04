# VADAFOK Studio 2.2.1

## Ziel

Fix für die Interaktion im Template Editor nach Einführung der neuen Template-Ordnerstruktur.

## Repariert

- Felder werden beim Anklicken nicht mehr aus alten Daten zurückgeladen.
- Hintergrundbild bleibt beim Anklicken/Verschieben erhalten.
- Felder lassen sich wieder auswählen.
- Felder lassen sich verschieben.
- Felder lassen sich an Kanten/Ecken skalieren.
- Änderungen werden in `data/templates/<Template>/template.json` gespeichert.

## Test

1. Template Editor öffnen.
2. Hintergrundbild setzen oder vorhandenes Template mit Bild öffnen.
3. Ein Feld anklicken.
4. Prüfen: Feld wird markiert.
5. Feld verschieben.
6. Feldgröße ändern.
7. SAVE TEMPLATE.
8. Studio neu starten.
9. Prüfen: Bild + Felder sind noch da.
10. Card Creator öffnen und Render testen.

## Git

Erst committen, wenn Bild und Feldbearbeitung stabil funktionieren.
