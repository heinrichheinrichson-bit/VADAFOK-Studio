# 2.18 RC1A – Stream Workflow Polish

## Ergänzungen gegenüber RC1
- Das Hauptfenster speichert seine zuletzt verwendete Größe, Position und den maximierten Zustand.
- Quick Caption speichert seine zuletzt verwendete Größe und Position dauerhaft.
- Benutzer dürfen Quick Caption weiterhin bewusst so klein ziehen, dass Status, Hilfe oder Aktionsleiste nicht sichtbar sind. Es wird keine Mindestgröße erzwungen.
- Nach erfolgreichem `SHOW` wird der Quick-Caption-Entwurf gelöscht.
- Bleibt Quick Caption nach dem SHOW-Versuch offen, wird der Entwurf als Sicherheitskopie behalten.

## Datenhaltung
Die Fensterzustände werden separat in `data/workspace_state.json` gespeichert. Bestehende Einstellungen, Roadmap, Ideas und andere Dokumente werden nicht überschrieben.
