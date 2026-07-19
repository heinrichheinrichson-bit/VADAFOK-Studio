VADAFOK QUICK CARDS – TRANSLATION SUGGESTION PATCH
==================================================

Ziel
----
Im Voice-Quick-Card-Vorschlagsfenster wird zusätzlich zum erkannten Text und
den bestehenden Quick-Card-Treffern eine englische DeepL-Übersetzung vorbereitet.

Sprachsteuerung
---------------
VADAFOK ONE / TWO / THREE  -> vorhandenen Quick-Card-Treffer übernehmen
VADAFOK TEXT               -> den von Whisper erkannten Originaltext übernehmen
VADAFOK TRANSLATE          -> die sichtbare vorbereitete Übersetzung übernehmen
VADAFOK SHOW               -> ausgewählten Text über den bestehenden OBS-Weg senden

Wichtige Sicherheitsregel
-------------------------
VADAFOK TRANSLATE funktioniert nur, solange das Vorschlagsfenster geöffnet ist.
Der Befehl verwendet exakt die dort sichtbare Übersetzung des dort angezeigten
Whisper-Textes.

Installation
------------
1. VADAFOK Studio beenden.
2. ZIP direkt über den Projektordner entpacken.
3. Vorhandene Dateien überschreiben.
4. DeepL-Key in Windows als Umgebungsvariable DEEPL_API_KEY hinterlegen.
5. VADAFOK Studio neu starten.

PowerShell, nur für die aktuelle Sitzung:
    $env:DEEPL_API_KEY="DEIN_DEEPL_KEY"

Dauerhaft für den Benutzer:
    [Environment]::SetEnvironmentVariable(
        "DEEPL_API_KEY",
        "DEIN_DEEPL_KEY",
        "User"
    )

Danach VADAFOK Studio vollständig neu starten.

Sprache
-------
Standardziel ist EN. Falls config_data bereits den Schlüssel
translation_target_language enthält, wird dessen Wert verwendet.

Fehlerverhalten
---------------
Fehlt der Key oder antwortet DeepL nicht, bleiben alle bisherigen Quick-Card-
Funktionen erhalten. Im Fenster steht dann, dass die Übersetzung nicht
verfügbar ist. Es wird niemals automatisch etwas an OBS gesendet.

Enthaltene Dateien
------------------
vadafok_studio/voice_control/foundation.py
vadafok_studio/voice_control/quick_card_voice.py
vadafok_studio/voice_control/voice_library.json
tests/test_quick_card_translation_selection.py
