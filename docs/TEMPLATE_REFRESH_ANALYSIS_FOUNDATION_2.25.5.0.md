# VADAFOK Studio 2.25.5.0 – Refresh Analysis Foundation

Basis: `93c037234a1c311f590ef80fb6bb2d1aeb0c0eee`

## Ziel

Der optionale RefreshProfiler erfasst zusätzlich zu Zählern und Laufzeiten
eine begrenzte, geordnete Ereignishistorie. Verschachtelte Gateway-Aufrufe
werden als Refresh-Ketten rekonstruiert.

## Neue Schnittstellen

```python
manager.refresh_analysis()
manager.refresh_analysis_text()
manager.reset_analysis()
```

`refresh_analysis()` liefert:

- geordnete Ereignisse
- Aufrufzahlen je Gateway
- Parent-/Root-Beziehungen
- rekonstruierte Top-Level-Ketten
- Fehlerkennzeichnung
- Information über verworfene ältere Ereignisse

Die Ereignishistorie ist standardmäßig auf 1000 Einträge begrenzt.
Profiling bleibt standardmäßig deaktiviert.

## Kompatibilität

Nicht verändert werden:

- Refresh-Reihenfolgen
- vorhandene Gateway-Methoden
- Ausnahmeverhalten
- normale Benutzeroberfläche
- bestehende Developer-View-API
- automatische Optimierung oder Batching
