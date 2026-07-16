# VADAFOK Studio 2.24.2.1 – Template Editor Controller Apply Fix

Der erste Apply-Patcher validierte einen zu großen Codebereich und erkannte
dadurch legitime `show_template_editor_page()`-Aufrufe in nachfolgenden
Methoden fälschlich als Fehler.

Die korrigierte Fassung prüft exakt nur den Methodenkörper von
`template_select()`.

Programmumfang und Controller-Logik bleiben unverändert.
