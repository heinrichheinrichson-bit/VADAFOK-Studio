# VADAFOK Studio – Project Structure

Stand: 2.19 RC1

Diese Übersicht dokumentiert die derzeit erkennbare Hauptstruktur. Sie ersetzt keine bestehende Architektur- oder Roadmap-Datei.

## Projektwurzel

- `run.py` – Startpunkt der Python-Anwendung.
- `Start VADAFOK Studio.bat` – Windows-Startskript.
- `requirements.txt` – allgemeine Python-Abhängigkeiten.
- `requirements_voice.txt` – zusätzliche Voice-/Whisper-Abhängigkeiten.
- `text_library.json` – Quick-Card-Texte als vollständige, häufig verwendete Aussagen.
- `caption_library.json` – Caption-bezogene Bibliotheksdaten.
- `scene_favorites.json` – gespeicherte Szenenfavoriten.
- `silent_director_presets.json` – Silent-Director-Presets.
- `ROADMAP.md` – historische Projekt-Roadmap/Skilltree; nicht überschreiben.
- `README.md` – Einstieg und Projektbeschreibung; derzeit teilweise historisch.

## `vadafok_studio/`

Hauptanwendung und Module. Dazu gehören unter anderem:

- zentrale Anwendung/UI
- OBS-Workflow und Controller
- Card Creator und Template Editor
- Live Card, Quick Cards und Banner-Workflow
- Voice Control, Voice Matcher und Whisper-Integration
- Workspace-/Fensterzustände
- zentrale Versionsinformation in `vadafok_studio/version.py`

## `data/`

Laufzeit- und Benutzerdaten, zum Beispiel:

- Workspace-Zustände
- Quick-Card-Favoriten und Recent-Verlauf
- weitere persistente UI- oder Workflow-Daten

Diese Dateien sollen nicht ohne Migrationsplan umbenannt oder verschoben werden.

## `docs/`

Aktuelle und historische Projektdokumentation:

- Vision und Entwicklungsregeln
- Roadmaps und Ideas
- Architektur und Workflows
- Voice-Control-Dokumentation
- RC-/Feature-Dokumente
- Test- und Release-Hinweise

Ziel des 2.19-Cleanups ist eine klare Trennung zwischen:

```text
docs/current/   (später möglich; aktuelle Referenzdokumente)
docs/history/   (historische RC- und Testunterlagen)
```

Die Einführung dieser Ordner erfolgt erst nach einer geprüften Inventarliste.

## `assets/`, `library/`, `styles/`, `tools/`

- `assets/` – UI- und Programm-Assets, zum Beispiel Icons.
- `library/` – inhaltliche Presets und weitere Bibliotheksressourcen.
- `styles/` – visuelle Styles und Style-Daten.
- `tools/` – Hilfsprogramme und Skripte.

## `exports/`

Vom Card Creator erzeugte Ausgaben und Vorschauen. Für 2.19 wird geprüft, welche Dateien bewusst als Beispiele versioniert werden und welche über `.gitignore` ausgeschlossen werden sollten.

## Cleanup-Regel

In RC1 wird nichts automatisch gelöscht oder verschoben. RC2 darf erst nach Prüfung der Datei-Verwendungen ein Archivpaket erzeugen.
