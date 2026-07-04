# VADAFOK Studio 0.7

## Hauptänderung

Studio 0.7 ist die erste echte Smart Caption Engine.

Nicht mehr:

```text
OBS Text + OBS Banner
```

Sondern:

```text
Banner + Text = fertiges PNG
```

OBS zeigt nur noch die Bildquelle:

```text
VADAFOK Caption Render
```

## Was neu ist

- smart_png rendert das aktuell gewählte Banner und den Text in eine fertige PNG.
- Der Text wird automatisch im Banner zentriert.
- OBS-Text ist für smart_png nicht mehr nötig.
- Das alte System `obs_text` bleibt als Fallback erhalten.
- Bannerwechsel aus der Library bleibt erhalten.
- Das Ergebnis wird gespeichert als:

```text
exports/caption_render.png
```

## OBS-Struktur

Empfohlen:

```text
VADAFOK Caption
├── VADAFOK Caption Render
├── VADAFOK Caption Text       optional / Fallback
└── VADAFOK Caption Banner     optional / Fallback
```

Für die neue Engine ist wichtig:

```text
VADAFOK Caption Render
```

Diese Quelle muss eine Bildquelle sein.

## Verwendung

1. In Studio ein Banner aus der Library wählen.
2. `USE AS CAPTION BANNER` klicken oder Banner doppelklicken.
3. Zu Live Card gehen.
4. Engine auf `smart_png` stellen.
5. Text schreiben.
6. SHOW klicken.

## Git

Erst committen, wenn 0.7 erfolgreich getestet wurde.
