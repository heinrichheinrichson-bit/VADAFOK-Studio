# 2.24.5.2 – Library Picker Runtime Return Fix

Doppelklick und `SHOW / USE` landen beide in derselben
Hintergrundübernahme.

Die Rückkehr zum Template Editor wird über drei Signale abgesichert:

1. Zustand des `LibraryController`;
2. Kompatibilitätsflag des Pickers;
3. Rückkehrseite `Template Editor`.

Damit ist die Rückkehr nicht mehr von einem einzelnen temporären Zustand
abhängig.
