# VADAFOK Studio 2.25.7.0 – Refresh Hotspot Analyzer

Basis: `2b591f7d0d287e1cf6e6115db47556375c50288d`

## Ziel

Die vorhandenen, passiv erfassten Gateway-Metriken werden als Hotspot-Rankings
ausgewertet. Die Analyse verändert weder Aufrufe noch Refresh-Reihenfolgen.

## Neue Schnittstellen

```python
manager.refresh_hotspot_analysis()
manager.refresh_hotspot_text()
```

`refresh_hotspot_analysis()` liefert:

- Gesamtzahl aller gemessenen Gateway-Aufrufe
- aufsummierte Gateway-Zeit
- Anzahl unterschiedlicher Gateways
- Anteil jedes Gateways an Aufrufzahl und Gateway-Zeit
- Ranking nach Gesamtzeit
- Ranking nach Häufigkeit
- Ranking nach Durchschnittszeit
- Ranking nach höchstem Einzelwert

Die Standardliste `gateways` ist nach Gesamtzeit sortiert.

## Einordnung der Zeitwerte

Verschachtelte Gateways werden weiterhin einzeln gemessen. Die aufsummierte
Gateway-Zeit ist deshalb eine Diagnosegröße und keine exklusive Wall-Clock-Zeit.
Dieses Verhalten entspricht der bestehenden Profiler-Semantik.

## Nicht enthalten

- keine Optimierung
- kein Batching
- kein Entfernen oder Zusammenfassen von Refreshes
- keine Änderung der Refresh-Reihenfolge
- keine neue GUI
- keine automatische Aktivierung
- keine Speicherung

Das Laufzeitverhalten des Template Editors bleibt unverändert.
