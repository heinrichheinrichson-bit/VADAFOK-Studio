# VADAFOK Studio 2.25.0.5 – Incremental Properties GUI Refresh

## Ziel

Die Properties-Seite des Template Editors wurde bei jedem Auswahlwechsel vollständig zerstört und neu aufgebaut. Dadurch entstand trotz korrekter Funktion ein kurzes sichtbares Aufblitzen.

## Änderung

Die Property-Widgets werden jetzt pro Properties-Container nur einmal erzeugt und anschließend wiederverwendet. Beim Wechsel zwischen „kein Feld ausgewählt“ und einer aktiven Auswahl werden lediglich zwei bestehende Ansichten ein- beziehungsweise ausgeblendet. Die bereits vorhandenen `tkinter`-Variablen liefern weiterhin sofort die Werte des aktuell ausgewählten Feldes.

Die Layers-Liste bleibt bei Auswahlwechseln weiterhin inkrementell: Nur Text und Hervorhebungszustand der vorhandenen Zeilen werden angepasst. Ein kurzes Farbwechseln der angeklickten Zeile ist die gewollte Auswahlrückmeldung und kein Neuaufbau.

## Unverändert

- Auswahlverhalten
- Mehrfachauswahl und Rahmenauswahl
- Smart Snap und Smart Guides
- Drag, Resize, Zoom und Pan
- automatisches Speichern
- Undo und Redo
- Template-Dateiformat
