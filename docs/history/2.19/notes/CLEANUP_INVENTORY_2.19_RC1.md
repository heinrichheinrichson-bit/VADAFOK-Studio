# 2.19 RC1 – Cleanup Inventory

Status: Inventar, noch keine Löschung

## In der Projektwurzel beobachtete Kandidaten

- `INSTALLIEREN_UND_TESTEN_2.16.7_RC1.txt`
- `INSTALLIEREN_UND_TESTEN_2.16.8_RC1A.txt`
- `INSTALLIEREN_UND_TESTEN_2.16.8_RC1B.txt`
- `INSTALLIEREN_UND_TESTEN_2.16.8_RC1C.txt`
- `INSTALLIEREN_UND_TESTEN_2.16.9_RC1.txt`
- `INSTALLIEREN_UND_TESTEN_2.17_RC1.txt`
- `FINALIZE_RELEASE_2.16.6.bat`
- `RELEASE_2.16.6.md`
- `VADAFOK_CODE_ONLY.zip`

## In `docs/` beobachtete Kandidaten

- `BANNER_WORKFLOW_2.17_RC1_APPEND.md`
- `QUICK_CARDS_WORKFLOW_2.16.9_RC1.md`
- `VOICE_CONTROL_2.16.7_RC1_APPEND.md`
- `VOICE_QUICK_CARDS_2.16.8_RC1A.md`
- `VOICE_QUICK_CARDS_2.16.8_RC1B.md`
- `VOICE_QUICK_CARDS_2.16.8_RC1C.md`

## Weitere Konsolidierungspunkte

- Mehrere Roadmap-Dateien: `ROADMAP.md`, `docs/ROADMAP.md`, `docs/MASTER_ROADMAP.md`.
- Root-README und docs-README enthalten historische Versionsstände.
- `docs/01_DEVELOPMENT_RULES.md` ist sehr kompakt; `PROJECT_RULES.md` ergänzt die inzwischen gemeinsam festgelegten Regeln.
- Export-Vorschaubilder im Repository müssen in RC2 einzeln als Beispiel oder generiertes Ergebnis klassifiziert werden.

## RC2-Prüfung vor Änderungen

Für jeden Kandidaten wird dokumentiert:

1. Wird die Datei durch Python- oder Batch-Code referenziert?
2. Enthält sie einzigartige historische Information?
3. Soll sie nach `docs/history/<version>/` verschoben werden?
4. Kann sie sicher entfernt werden?
5. Muss `.gitignore` angepasst werden?

Ohne diese Prüfung wird nichts gelöscht.
