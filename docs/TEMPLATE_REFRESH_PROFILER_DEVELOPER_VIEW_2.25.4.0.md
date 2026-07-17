# VADAFOK Studio 2.25.4.0 – RefreshProfiler Developer View

Basis: `4820b57a458fe0a76ee16f6956794ff062a62d94`

## Ziel

Die in 2.25.3.0 eingeführten Messwerte werden über eine stabile,
GUI-unabhängige Entwickleransicht nutzbar gemacht.

## Schnittstellen

```python
manager.set_profiling(True)
manager.refresh_developer_view()
manager.refresh_developer_text()
manager.reset_profile()
manager.set_profiling(False)
```

`refresh_developer_view()` liefert Zähler und aggregierte Laufzeiten als
detached Dictionary. `refresh_developer_text()` liefert dieselben Werte in
einer kompakten Textansicht.

## Nicht enthalten

- kein neuer Menüpunkt
- keine Toolbar- oder Statusleistenänderung
- keine automatische Aktivierung
- keine Speicherung
- keine Änderung der Refresh-Reihenfolgen
- keine Optimierung oder Zusammenfassung von Refreshes

Dadurch bleibt der normale Benutzerbetrieb unverändert.
