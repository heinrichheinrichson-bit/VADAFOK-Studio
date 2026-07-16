# VADAFOK Studio 2.22.3 – Foundation – Basic Tests

## Automatische Prüfungen

Die neue `unittest`-Suite prüft:

- zentrale Versionswerte;
- Ableitung von Fenstertitel, Sidebar und Windows-App-ID;
- zentrale Logging-Konfiguration;
- Log-Rotation;
- globalen Python-, Thread- und Tkinter-Exception-Hook;
- Schreiben in die Logdatei;
- zentrale Versions- und Logging-Verwendung in `app.py`;
- erforderliche `.gitignore`-Einträge;
- Python-Syntax zentraler Dateien.

Zusätzlich wird das gesamte Paket `vadafok_studio` mit `compileall` geprüft.

## Korrektur aus 2.22.2

Der Tkinter-Callback-Hook wird an `tkinter.Tk.report_callback_exception`
angebunden. Dadurch entsteht beim Start kein falscher Logging-Fehler mehr.

## Repository-Hygiene

Generierte Dateien werden aus der Git-Verfolgung entfernt, lokal jedoch nicht
gelöscht:

- `.idea`;
- `__pycache__`;
- Laufzeitlogs;
- temporäre `app.py`-Backups;
- generiertes Caption-Exportbild.
