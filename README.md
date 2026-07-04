# VADAFOK Studio 0.8

## Hauptänderung

Studio 0.8 verfeinert die Smart Caption Engine mit einer **Safe Area**.

Problem aus 0.7:
Lange Texte wurden zwar automatisch kleiner, konnten aber noch in dekorative Rahmenbereiche des Banners ragen.

Lösung in 0.8:
Der Text wird nur noch in einem geschützten Innenbereich gerendert.

## Neu

Im Bereich **Caption Engine** gibt es neue Werte:

```text
Safe Left %
Safe Right %
Safe Top %
Safe Bottom %
```

Diese Werte bestimmen, wie viel Abstand vom Rand des Banners freigehalten wird.

Empfohlener Startwert:

```text
Left: 12
Right: 12
Top: 24
Bottom: 24
```

Wenn Text zu sehr in den Rahmen läuft:
- Left/Right erhöhen
- Top/Bottom erhöhen

Wenn der Text zu klein wird:
- Werte etwas verringern

## Architektur

Weiterhin gilt:

```text
Banner + Text = fertiges PNG
```

OBS zeigt nur:

```text
VADAFOK Caption Render
```

## Test

1. Banner wählen.
2. Engine auf `smart_png`.
3. Lange Caption testen:

```text
THE SHOW WILL BEGIN SHORTLY
```

4. Safe-Area-Werte anpassen.
5. SHOW erneut drücken.

## Git

Erst committen, wenn 0.8 erfolgreich getestet wurde.
