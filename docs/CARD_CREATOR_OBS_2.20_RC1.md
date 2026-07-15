# VADAFOK Studio 2.20 RC1 – Card Creator → OBS Live Display

**Basis-Commit:** `8619d5a7e765395c7c006224d4c9eb3c6ccfda8f`

## Ziel

Der Card Creator erhält einen zusätzlichen Weg neben dem bestehenden Export:

- **RENDER CARD / Export:** bleibt unverändert.
- **SHOW IN OBS:** rendert die aktuelle Karte mit dem ausgewählten Exportprofil und zeigt sie unmittelbar in OBS.

## Technische Anbindung

RC1 verwendet bewusst bereits vorhandene Komponenten:

- `card_render_to_file(final=True)` für das aktuelle Template und Exportprofil;
- die vorhandene OBS-Verbindung;
- `scene_card_source` als bestehende OBS-Bildquelle;
- `OBSController.set_image_file(...)`;
- `OBSController.enable_source(...)`.

Es wird keine zweite Rendering- oder OBS-Infrastruktur eingeführt.

## Grenzen von RC1

- kein automatisches Ausblenden;
- kein Timer;
- kein zusätzlicher HIDE-Button;
- keine neue OBS-Quelle wird automatisch erstellt;
- die konfigurierte Scene-Card-Quelle muss in der aktuellen OBS-Szene vorhanden sein.

## Sicherheit

Das Bild wird erst gerendert und dann eingeblendet. Bei fehlender OBS-Verbindung,
fehlender Quelle oder Renderfehler erscheint eine verständliche Fehlermeldung.
Der normale Exportweg bleibt unberührt.
