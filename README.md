# VADAFOK Studio 1.3

## Ziel

Studio 1.3 beginnt mit der Layout-Engine.

Der Banner Editor bleibt wie bisher nutzbar, aber intern wird vorbereitet, dass später auch Templates mit mehreren Textfeldern möglich werden.

## Neu

- Neues Modul:

```text
vadafok_studio/core/layout_engine.py
```

- Erste LayoutField-Struktur als Grundlage für spätere Multi-Field-Templates.
- Bannerprofile können intern als Layout-Feld behandelt werden.
- Neuer Button im Banner Editor:

```text
RESET STYLE
```

## Reset-Logik

```text
RESET AREA
```

setzt nur den Textbereich/Rahmen zurück.

```text
RESET STYLE
```

setzt nur die Profilwerte zurück:

- Font
- Font Size
- Text Color
- Stroke Color
- Stroke Width
- Uppercase

Der Textbereich bleibt dabei erhalten.

## Test

1. Banner Editor öffnen.
2. Banner auswählen.
3. Schriftgröße/Farbe/Stroke ändern.
4. RESET STYLE drücken.
5. Prüfen, ob die Werte auf Standard zurückgehen.
6. Prüfen, ob der Rahmen/Textbereich unverändert bleibt.
7. Live Card mit `smart_png` testen.
8. Prüfen, ob alles weiterhin in OBS korrekt angezeigt wird.

## Git

Erst committen, wenn RESET STYLE und Live Card stabil funktionieren.
