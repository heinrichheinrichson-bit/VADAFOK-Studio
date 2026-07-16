# VADAFOK Studio 2.24.5 – Foundation – Library Controller

Der temporäre Picker-Zustand wird nicht mehr von den Library-Widgets oder
`app.py` verwaltet, sondern vom neuen `LibraryController`.

## Template-Hintergrund-Workflow

- `SET BACKGROUND FROM LIBRARY` öffnet die visuelle Library direkt in
  `Templates`.
- Einfacher Klick wählt ein Bild und zeigt die große Vorschau.
- Doppelklick führt die vorhandene Standardaktion aus.
- `SHOW / USE` führt dieselbe Standardaktion aus.
- Im Picker-Modus wird das Bild übernommen und danach automatisch zum
  Template Editor zurückgekehrt.
- Im normalen Library-Modus bleibt das bisherige Verhalten bestehen.

## Architektur

Neu:

`vadafok_studio/library/controller.py`

Damit ist neben Card Creator und Template Editor nun auch der erste
Library-Workflow aus `app.py` ausgelagert.
