# VADAFOK Studio 2.21 RC2 – Custom Display Duration

Die vorhandene Dauer-Auswahl wird ergänzt um:

- `Custom...`
- freie Eingabe von 1 bis 3600 Sekunden

Das Eingabefeld ist nur sichtbar, wenn `Custom...` gewählt ist.

## Regeln

- nur positive ganze Sekunden;
- Minimum 1 Sekunde;
- Maximum 3600 Sekunden;
- ungültige Werte zeigen eine verständliche Warnung;
- bei ungültigem Wert wird die OBS-Quelle nicht eingeblendet;
- erneutes SHOW startet den Custom-Timer neu;
- HIDE beendet ihn sofort;
- der letzte gültige Custom-Wert bleibt während der Programmsitzung erhalten.
