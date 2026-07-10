# Studio 2.3.0 Rendering Foundation

Basis: die vom Nutzer erneut hochgeladene stabile Version 2.2.1.

## Ziel dieser Version

Diese Version ist absichtlich ein kleiner, konservativer Architektur-Schritt.

Sie führt `vadafok_studio/core/preview_engine.py` ein:

- `PreviewTransform`
- `fit_to_box`
- `load_rgba`
- `pil_to_tk_data`
- `status_for_path`

Dadurch gibt es erstmals eine zentrale Stelle für:

- Bild laden
- Bild in Canvas einpassen
- Originalkoordinaten in Bildschirmkoordinaten umrechnen
- Bildschirmbewegungen zurück in Originalkoordinaten umrechnen

## Wichtig

2.3.0 soll möglichst wenig sichtbares Verhalten ändern.
Die stabile Funktionalität von 2.2.1 soll erhalten bleiben.

## Nächste Schritte

- 2.3.1: Template Editor vollständig auf `PreviewTransform` umstellen.
- 2.3.2: Card Creator Vorschau auf dieselbe Skalierung umstellen.
- 2.3.3: Banner Editor ebenfalls auf `PreviewTransform` umstellen.
- Danach erst Anti-Flicker gezielt einbauen.

## Warum so vorsichtig?

Die Zwischenversionen 2.2.2 bis 2.2.4 haben gezeigt, dass große gleichzeitige Änderungen neue UI-Fehler erzeugen.
Ab jetzt wird jede Rendering-Änderung kleiner und einzeln testbar gebaut.
