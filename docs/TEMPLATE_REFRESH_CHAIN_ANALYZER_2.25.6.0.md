# VADAFOK Studio 2.25.6.0 – Refresh Chain Analyzer

Basis: `7f027dc492c4ba493e98c3ddd31cef6c95cb772b`

## Ziel

Die in 2.25.5.0 aufgezeichneten Refresh-Ketten werden passiv nach ihrer
Struktur gruppiert. Identische Ketten erhalten Häufigkeits- und Laufzeitwerte.

## Neue Schnittstellen

```python
manager.refresh_chain_analysis()
manager.refresh_chain_text()
```

`refresh_chain_analysis()` liefert unter anderem:

- Gesamtzahl aufgezeichneter Ketten
- Zahl eindeutiger Kettenstrukturen
- stabile Struktursignatur
- Häufigkeit je Kette
- Gesamt-, Durchschnitts-, Minimum- und Maximumlaufzeit
- Fehleranzahl
- Gateway-Reihenfolge einschließlich Verschachtelungstiefe

Die Gruppen werden nach Häufigkeit, Gesamtzeit und Signatur sortiert.

## Nicht enthalten

- keine Optimierung
- kein Batching
- kein Entfernen oder Zusammenfassen von Refreshes
- keine neue GUI
- keine automatische Aktivierung
- keine Speicherung

Das Laufzeitverhalten des Template Editors bleibt unverändert.
