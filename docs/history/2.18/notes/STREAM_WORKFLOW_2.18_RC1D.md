# VADAFOK Studio 2.18 RC1D – Central Draft Discard Fix

RC1D behebt ausschließlich die gemeinsame Entwurfslogik von SHOW, RESET und STOP.

- SHOW, RESET und STOP verwenden denselben zentralen Löschpfad.
- Der periodische Draft-Monitor darf während dieser Aktionen keinen Text zurückschreiben.
- X und Escape behalten den Entwurf weiterhin.
- Bestehende Dokumentation wird nicht ersetzt.
