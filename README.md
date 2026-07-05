# VADAFOK Studio 2.5.9.1

## Ziel

Fix für Multi Selection.

## Problem in 2.5.9

`Shift + Linksklick` wurde auf deinem System nicht zuverlässig erkannt.

## Repariert

- Shift wird jetzt zusätzlich über KeyDown/KeyUp gemerkt.
- Ctrl wird ebenfalls unterstützt.
- Multi Selection funktioniert jetzt mit:
  - `Shift + Klick`
  - `Ctrl + Klick`

## Test

1. Template Editor öffnen.
2. Ein Feld normal anklicken.
3. `Shift + Klick` auf zweites Feld.
4. Prüfen: beide Felder markiert.
5. `Shift + Klick` auf markiertes Feld.
6. Prüfen: Feld wird abgewählt.
7. Dasselbe mit `Ctrl + Klick` testen.
8. Delete Field bei mehreren Feldern testen.
9. Smart Guides, Copy Field und Einzelauswahl kurz prüfen.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.5.9.1 - Fix multi selection modifier handling"
git push
```

## Commit-Beschreibung

```text
v2.5.9.1 - Fix multi selection modifier handling

- Improved Shift/Ctrl detection for template field multi selection
- Added explicit KeyDown/KeyUp modifier tracking
- Added Ctrl+Click as alternate multi-select input
- Existing Smart Guides, Copy Field and single-field editing preserved
```
