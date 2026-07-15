# VADAFOK Studio 2.20 RC2 – Card Creator OBS Control

**Basis-Commit:** `15a33c47c7260ded846518b7f710d0ab50284ea3`

## Ergänzungen

- `HIDE FROM OBS` blendet dieselbe Scene-Card-Bildquelle aus.
- Eine Statuszeile zeigt:
  - `NOT CONNECTED`
  - `READY`
  - `LIVE`
  - `HIDDEN`
  - `ERROR`
- SHOW und HIDE werden bei fehlender OBS-Verbindung deaktiviert.
- Der Status wird regelmäßig aktualisiert, solange der Card Creator geöffnet ist.
- Der bestehende Exportweg bleibt unverändert.

## Technische Anbindung

RC2 verwendet weiterhin:

- die vorhandene OBS-Verbindung;
- die Einstellung `scene_card_source`;
- die aktuelle OBS-Programmszene;
- `OBSController.enable_source(...)`;
- die bestehende Renderfunktion des Card Creators.

## Nicht enthalten

- keine Timer;
- kein automatisches Ausblenden;
- keine neue OBS-Quelle;
- keine Voice-Befehle für SHOW/HIDE.
