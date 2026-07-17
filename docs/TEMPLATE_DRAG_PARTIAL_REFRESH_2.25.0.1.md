# VADAFOK Studio 2.25.0.1 – Template Drag Partial Refresh

## Ziel

Das Verschieben und Skalieren von Feldern im Template Editor soll flüssiger werden, ohne Smart Snap, Smart Guides, Zoom, Pan, Buttons oder bestehende Workflows zu verändern.

## Ursache

`template_update_fields_overlay()` wurde bei jeder Mausbewegung aufgerufen. Die Funktion zeichnete nicht nur das Canvas-Overlay neu, sondern:

- prüfte bei jeder Bewegung erneut den Hintergrundstatus auf dem Dateisystem,
- aktualisierte den Status-Text,
- zerstörte die komplette Layers-Liste,
- erzeugte alle Layer-Widgets erneut.

Das erklärte sowohl das sichtbare Flackern der Layers-Liste als auch einen Teil der Verzögerung beim Ziehen.

## Änderung

`template_update_fields_overlay()` unterstützt nun zwei gezielte Schalter:

- `refresh_layers`
- `refresh_status`

Während `<B1-Motion>` werden beide deaktiviert. Dadurch aktualisiert die Drag-Schleife nur noch:

1. Feldkoordinaten,
2. Canvas-Overlay,
3. Smart Snap,
4. Smart Guides.

Beim Loslassen wird der Status einmal aktualisiert. Die Layers-Liste wird nicht unnötig neu aufgebaut, da sich beim Ziehen weder Reihenfolge noch Name, Sichtbarkeit oder Sperrstatus ändern.

## Bewusst unverändert

- Smart Snap
- Smart Guides
- Zoom
- Pan
- Layer-Reihenfolge
- Properties
- Template-Dateiformat
- alle Buttons und Workflows
