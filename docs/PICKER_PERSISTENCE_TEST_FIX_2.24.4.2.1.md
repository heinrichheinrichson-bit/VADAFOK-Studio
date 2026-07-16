# VADAFOK Studio 2.24.4.2.1 – Picker Persistence Test Fix

Der Test erwartete den Ausdruck für `library_return_page` in einer bestimmten
Zeilenformatierung.

Die Implementierung war bereits korrekt:

`getattr(self, "library_return_page", None) == "Template Editor"`

Der neue Test prüft die relevanten Bestandteile unabhängig von
Zeilenumbrüchen und Einrückung.

Programmcode wird nicht verändert.
