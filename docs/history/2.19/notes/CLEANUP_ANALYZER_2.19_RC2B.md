# Cleanup Analyzer 2.19 RC2B

RC2B korrigiert die Ermittlung des Projektordners unter Windows.

- keine Übergabe eines Pfads mit abschließendem Backslash aus der Batch-Datei
- Verwendung von `$PSScriptRoot`
- defensive Pfadbereinigung und Validierung
- keine Verschiebung oder Löschung bestehender Projektdateien
