# VADAFOK Studio 2.25.9.0 – Refresh Flow Analyzer

Basis: `02d412da2ccbdbf2fabb9fd3cf66ca1fa80529a1`

## Ziel

Komplette aufgezeichnete Refresh-Ketten werden passiv als Flows gruppiert und statistisch ausgewertet.

## Neue Schnittstellen

```python
manager.refresh_flow_analysis()
manager.refresh_flow_text()
```

Die Analyse liefert vollständige Flow-Signaturen, Start- und End-Gateway, Gateway-Anzahl, maximale Verschachtelungstiefe, Häufigkeit, Laufzeitstatistiken sowie Fehleranzahl und Fehlerquote.

## Semantik

Ein Flow entspricht genau einer rekonstruierten Top-Level-Kette aus `analysis_snapshot()`. Identische Reihenfolge und Tiefenstruktur werden gruppiert. Es werden keine unabhängigen Top-Level-Aufrufe miteinander verbunden.

## Nicht enthalten

- keine Optimierung
- kein Batching
- keine Änderung der Refresh-Reihenfolge
- keine neue GUI
- keine automatische Aktivierung
- keine Persistenz

Das Laufzeitverhalten des Template Editors bleibt unverändert.
