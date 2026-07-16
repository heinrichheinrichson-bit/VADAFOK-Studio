# VADAFOK Studio 2.24.1.1 – Controller Test Migration

Die beiden bestehenden Partial-Refresh-Tests wurden an die neue Architektur
angepasst.

Sie prüfen weiterhin:

- kein vollständiger Seiten-Refresh;
- gezielte Recent-Aktualisierung;
- gezielte All-Templates-Aktualisierung;
- Formular- und Vorschau-Refresh.

Die Prüfungen erfolgen jetzt dort, wo die Logik tatsächlich liegt:

`vadafok_studio/card_creator/controller.py`

Programmcode wird nicht verändert.
