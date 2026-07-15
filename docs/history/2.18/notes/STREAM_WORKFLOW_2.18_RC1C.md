# VADAFOK Studio 2.18 RC1C – Stream Workflow Final Fix

## Basis

Dieses Overlay wird über **VADAFOK Studio 2.18 RC1B** installiert.

## Korrektur

Der Quick-Caption-Entwurf wird beim bestehenden SHOW-Ablauf jetzt sofort aus dem Entwurfsspeicher entfernt. Während der Sendevorgang läuft, ist die automatische Entwurfssynchronisierung pausiert.

- Schließt der bestehende SHOW-Ablauf das Quick-Caption-Fenster, bleibt der Entwurf leer.
- Bleibt das Fenster offen, wird der sichtbare Text als Sicherheitsentwurf wiederhergestellt.

## Unveränderte Semantik

- X: Entwurf behalten
- Escape: Entwurf behalten
- Reset: Entwurf löschen
- Stop: Entwurf löschen
- Show: nach erfolgreicher Ausgabe Entwurf löschen
