VADAFOK Studio 2.29.0.0 - Launcher Build Fix 1

Ursache des Fehlers:
PyInstaller legte die SPEC-Datei in launcher_build ab und suchte die relative
Versionsdatei deshalb irrtuemlich unter launcher_build\launcher\version_info.txt.

Dieser Fix verwendet fuer Quellcode, Icon und Versionsdatei absolute Pfade.

Installation:
1. ZIP in den VADAFOK-Studio-Hauptordner entpacken.
2. BUILD_VADAFOK_STUDIO_EXE.bat ersetzen lassen.
3. BUILD_VADAFOK_STUDIO_EXE.bat erneut starten.

Der fehlgeschlagene Ordner launcher_build wird beim neuen Versuch automatisch
geloescht und sauber neu erstellt.
