## Zukunftsidee – Card Creator / Template direkt in OBS anzeigen

### Ausgangssituation
Im Template Editor werden Felder für Streampläne, Wochenpläne und ähnliche Karten definiert. Im Card Creator werden die aktuellen Inhalte eingetragen und über Exportprofile in verschiedene Bildformate gerendert.

### Geplanter Workflow
Eine im Card Creator aktuell erzeugte Karte soll optional direkt als länger sichtbares OBS-Overlay angezeigt werden können, ohne sie zuerst manuell zu exportieren und anschließend in OBS auszuwählen.

Möglicher Ablauf:

`Card Creator → Rendern → Show in OBS → Dauer oder manuelles Hide`

### Anforderungen
- Das bestehende Export-System bleibt unverändert erhalten.
- Für OBS wird automatisch ein geeignetes Broadcast-/Overlay-Format gerendert.
- Längere Anzeigezeiten wie 60 Sekunden, mehrere Minuten oder „bis Hide“ sind möglich.
- OBS bleibt für Szenen, Quellen und Audiomischung zuständig; VADAFOK ergänzt den schnellen Asset-Workflow.
- Die Architektur soll später optional auch Bilder, Templates und kurze Sound-Events über einen gemeinsamen OBS-Display-Manager unterstützen.

### Status
Idee für eine spätere eigene Version. Nicht Bestandteil von 2.18 RC1.
