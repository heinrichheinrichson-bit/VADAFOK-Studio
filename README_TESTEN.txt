VADAFOK Studio – Sound Favorites Editor Modular Refactor

Status: working towards the next release; no version number assigned yet.
Base: 2.29.0.3

Installation:
1. VADAFOK Studio schließen.
2. Den Inhalt dieses ZIP-Archivs in den Projektordner kopieren.
3. Vorhandene Dateien ersetzen lassen.

Tests:
1. python -m unittest discover -s tests -v
2. EXE neu bauen.
3. Live Card öffnen.
4. "FAVORITEN BEARBEITEN" öffnen.
5. Alle vier Namen und Dateien prüfen/ändern.
6. Abbrechen prüfen (keine Änderung).
7. Speichern prüfen (Änderung bleibt erhalten).
8. Einen Favoriten auswählen und SHOW/RESET/STOP testen.
9. F8 bzw. Sprachbefehl "Live Card" prüfen: weiterhin kompaktes Quick Caption Fenster.

Automatischer Teststand in der Entwicklungsumgebung:
226 Tests erfolgreich.
