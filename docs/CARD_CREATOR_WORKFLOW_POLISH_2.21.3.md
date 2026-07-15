# VADAFOK Studio 2.21.3 – Card Creator Workflow Polish

## Änderungen

- Die zuletzt gewählte Display-Dauer wird dauerhaft gespeichert.
- Der letzte gültige Custom-Wert wird dauerhaft gespeichert.
- Die Werte werden beim nächsten Programmstart wiederhergestellt.
- Custom-Eingaben werden bereinigt:
  - `00120` wird zu `120`
  - ` 60 ` wird zu `60`
  - `060` wird zu `60`
- Bei Custom-Timern zeigt der OBS-Status ausdrücklich `CUSTOM`.
- Dropdown und Custom-Eingabe sind optisch enger gruppiert.

## Speicherort

Die Einstellungen werden benutzerspezifisch gespeichert:

`~/.vadafok_studio/card_creator_obs_settings.json`

Andere VADAFOK-Konfigurationsdateien werden nicht verändert.
