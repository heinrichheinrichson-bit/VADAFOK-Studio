# VADAFOK Studio 2.22.2 – Foundation – Logging

## Zentraler Logger

Neues Modul:

`vadafok_studio/logging_setup.py`

## Logdateien

Die Dateien werden im Projektordner unter `logs/` angelegt:

- `vadafok_studio.log`
- `vadafok_studio.log.1`
- `vadafok_studio.log.2`
- `vadafok_studio.log.3`

Rotation erfolgt bei 2 MB pro Datei. `logs/` wird von Git ignoriert.

## Protokollierte Startinformationen

- VADAFOK-Version
- Python-Version
- Betriebssystem
- Python-Executable
- Arbeitsordner
- Prozess-ID
- Pfad der Logdatei

## Fehlererfassung

Global erfasst werden:

- unbehandelte Fehler im Hauptthread;
- unbehandelte Fehler in Worker-Threads;
- unbehandelte Tkinter-Callback-Fehler.

Bestehende Workflows und vorhandene Fehlermeldungen werden nicht verändert.
