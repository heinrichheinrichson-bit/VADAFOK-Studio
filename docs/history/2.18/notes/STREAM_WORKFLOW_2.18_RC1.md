# 2.18 RC1 – Stream Workflow

## Ziel
Der Start eines Streams und die spontane Kommunikation über Quick Caption werden komfortabler, ohne neue komplexe Funktionen einzuführen.

## Umsetzung
- `OBS Workflow` ist nach dem Programmstart automatisch die Startseite.
- Nicht gesendeter Quick-Caption-Text bleibt beim Schließen innerhalb der laufenden Programmsitzung erhalten.
- `RESET` löscht den Entwurf bewusst.
- `SHOW` verwendet weiterhin den bestehenden OBS-Sendeweg und verwirft danach den Entwurf.
- Quick Caption zeigt den aktuellen Voice-Status direkt im Fenster.
- Quick Caption verwendet eine einheitliche Aktionsleiste: `SHOW`, `RESET`, `STOP`.
- Die bereits vorhandene kontextabhängige Voice-Hilfe bleibt aktiv.

## Datenhaltung
Der Quick-Caption-Entwurf wird nur im Arbeitsspeicher behalten. Nach dem vollständigen Beenden von VADAFOK wird er nicht dauerhaft gespeichert.

## Sicherheit
Es gibt keinen neuen OBS-Sendeweg. Maus, Enter und Sprachbefehl nutzen weiterhin die vorhandene Quick-Caption-Sendeaktion.
