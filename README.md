
# VADAFOK Studio 0.5

## Start

```bat
py -m pip install -r requirements.txt
py run.py
```

## Neu in 0.5

- Caption-Banner kann jetzt direkt aus der Library gewechselt werden.
- Neue OBS-Quelle in den Einstellungen: `Caption Banner Source`
- Standardname: `VADAFOK Caption Banner`
- Doppelklick auf Asset in `Banners` setzt dieses Bild als Caption-Banner.
- Button `USE AS CAPTION BANNER` setzt jedes ausgewählte Bild als Caption-Banner.
- `SHOW` in Live Card verwendet das zuletzt gewählte Banner automatisch.

## OBS-Voraussetzung

In der Gruppe:

```text
VADAFOK Caption
├── VADAFOK Caption Text
└── VADAFOK Caption Banner
```

Die Bildquelle muss exakt so heißen:

```text
VADAFOK Caption Banner
```

Oder du passt den Namen im Studio an:

`OBS Connection` → `Caption Banner Source`

## Wichtig

Wenn deine Quellen in OBS richtig ausgerichtet sind, sperre sie mit dem Schloss-Symbol:

- VADAFOK Caption
- VADAFOK Caption Text
- VADAFOK Caption Banner

Dann bleibt die Position stabil.
