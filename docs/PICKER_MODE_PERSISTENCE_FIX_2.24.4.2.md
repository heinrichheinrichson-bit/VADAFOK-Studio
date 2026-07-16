# VADAFOK Studio 2.24.4.2 – Picker Mode Persistence Fix

## Ursache

`show_library()` baut die Library-Oberfläche neu auf und kann dabei temporären
Picker-Zustand zurücksetzen.

## Korrektur

- Picker-Modus wird erst nach `show_library()` und nach dem Öffnen des Ordners
  `Templates` gesetzt.
- Rückkehrziel `Template Editor` wird ebenfalls danach gesetzt.
- Die Übernahme erkennt zusätzlich das Rückkehrziel als Picker-Signal.

Damit funktionieren Klick, Doppelklick und `SHOW / USE` wieder als
Übernahmepfade mit automatischer Rückkehr.
