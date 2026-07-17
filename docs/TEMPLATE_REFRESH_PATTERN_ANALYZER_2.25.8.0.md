# VADAFOK Studio 2.25.8.0 – Refresh Pattern Analyzer

Basis: `aa1c3ff53e5b650bd6b8552f3fe2a5ba7b5fdee6`

## Ziel

Die bereits aufgezeichneten Refresh-Ketten werden passiv auf wiederkehrende
Parent-Child-Übergänge untersucht.

## Neue Schnittstellen

```python
manager.refresh_pattern_analysis()
manager.refresh_pattern_text()
```

`refresh_pattern_analysis()` liefert:

- Gesamtzahl analysierter Ketten
- Gesamtzahl der Parent-Child-Übergänge
- Zahl eindeutiger Übergänge
- stabile Übergangssignaturen
- Häufigkeit je Übergang
- Anteil eines Ziels an allen Ausgängen derselben Quelle
- gruppierte Ausgangsstatistiken je Gateway
- eingehende Übergangszahlen je Ziel

## Semantik

Ein Übergang entsteht nur zwischen einem aufgezeichneten Gateway und seinem
direkten Parent. Unabhängige Top-Level-Aufrufe werden nicht künstlich als
zeitliche Sequenz verbunden.

## Nicht enthalten

- keine Optimierung
- kein Batching
- keine Änderung der Refresh-Reihenfolge
- keine Änderung am Event-Limit
- keine neue GUI
- keine automatische Aktivierung
- keine Speicherung

Das Laufzeitverhalten des Template Editors bleibt unverändert.
