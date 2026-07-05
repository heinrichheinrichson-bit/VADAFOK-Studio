# VADAFOK Studio 2.7.4.1

## Hotfix

Template Editor Keyboard Shortcuts wurden bisher global ausgelöst.

Repariert:

- Delete / Backspace öffnen keine Template-Editor-Meldung mehr in anderen Bereichen.
- Texteingaben in Live Card und anderen Bereichen funktionieren wieder normal.
- Template Editor Shortcuts funktionieren nur noch im Template Editor.
- Shortcuts greifen nicht mehr in Textfeldern / Eingabefeldern.

## Test

Siehe `docs/RELEASE_CHECKLIST.md`.

## Git nach erfolgreichem Test

```bash
git add .
git commit -m "v2.7.4.1 - Fix Template Editor shortcut scope"
git push
```
