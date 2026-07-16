# VADAFOK Studio 2.22.1 – Foundation – Central Versioning

## Ziel

`vadafok_studio/version.py` ist die einzige Quelle für die aktuelle
Laufzeitversion.

Zentralisiert werden:

- Fenstertitel
- Sidebar-Version
- Windows AppUserModelID

Historische Dokumente behalten ihre damaligen Versionsnummern.

## Sicherheit

Der Apply-Patcher:

1. akzeptiert unterschiedliche Leerzeichen und Zeilenumbrüche;
2. erwartet für jede alte Laufzeitangabe genau eine Fundstelle;
3. erstellt vor der Änderung eine Sicherheitskopie;
4. prüft alle neuen Referenzen;
5. prüft, dass `2.16.5.1` aus `app.py` verschwunden ist;
6. kompiliert `app.py` und `version.py`;
7. stellt `app.py` bei einem Syntaxfehler automatisch wieder her.
