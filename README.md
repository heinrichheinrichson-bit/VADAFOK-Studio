# VADAFOK Studio 1.1.1

## Ziel

Anti-Flicker-Patch für den Banner Editor.

## Geändert

- Bannerbild wird beim Ziehen nicht mehr ständig neu geladen.
- Beim Ziehen wird nur noch der goldene Overlay-Rahmen aktualisiert.
- Sample-Text und Anfasser werden ohne Banner-Neuladen aktualisiert.
- Cursor-Verbesserungen aus 1.1 bleiben erhalten.
- OBS-Robustheit aus 1.1 bleibt erhalten.

## Test

1. Banner Editor öffnen.
2. Banner auswählen.
3. Goldenen Rahmen verschieben.
4. An Ecken/Kanten ziehen.
5. Prüfen: Das Banner sollte nicht mehr stark wegflackern.
6. Profil speichern.
7. Studio neu starten.
8. Prüfen, ob der Rahmen erhalten bleibt.
9. Live Card mit `smart_png` testen.

## Git

Erst committen, wenn das Flackern weg oder deutlich besser ist.
