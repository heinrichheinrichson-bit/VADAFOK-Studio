VADAFOK STUDIO 2.27.0.5
========================

WICHTIGSTE KORREKTUR
--------------------
Der neue Übersetzungsbefehl wurde jetzt auch in die echte Windows-
System.Speech-Grammatik eingebaut.

Damit kennt der Listener nun unter anderem:
- VADAFOK ENGLISH
- VADAFOK ENGLISCH
- VADAFOK ENGLISH TEXT
- VADAFOK TRANSLATE
- VADAFOK TRANSLATION

INSTALLATION
------------
1. VADAFOK Studio schließen.
2. ZIP direkt nach
   F:\Vadafok Studio\VADAFOK_Studio
   entpacken.
3. Vorhandene Dateien ersetzen.
4. Optional INSTALL_CERTIFICATES_2.27.0.5.bat ausführen.
5. VADAFOK über Start VADAFOK Studio.bat starten.

TEST
----
1. VADAFOK QUICK CARD sagen.
2. "Das war knapp." sagen.
3. Warten, bis "That was close." sichtbar ist.
4. VADAFOK ENGLISH sagen.
5. Das Vorschlagsfenster muss schließen.
6. Im Quick-Caption-Textfeld muss "That was close." stehen.
7. VADAFOK SHOW sagen.

WORAN MAN DEN RICHTIGEN BEFEHL ERKENNT
--------------------------------------
Im Voice-Status beziehungsweise Last-Heard-Bereich muss der erkannte feste
Befehl erscheinen. Zusätzlich setzt die Software beim Übersetzungszweig kurz:
COMMAND HEARD · ... · selecting translation

ROLLBACK MIT GIT BASH
---------------------
git restore vadafok_studio/version.py
git restore vadafok_studio/tools/voice_listener.ps1
git restore vadafok_studio/voice_control/foundation.py
git restore vadafok_studio/voice_control/quick_card_voice.py
git restore vadafok_studio/voice_control/voice_library.json
git restore vadafok_studio/translator
rm -f INSTALL_CERTIFICATES_2.27.0.5.bat
rm -f requirements_translation.txt
rm -f tests/test_voice_listener_english_command.py
rm -f tests/test_english_command_release.py
rm -f tests/test_deepl_ssl.py
rm -f tests/test_translation_runtime.py

Danach:
git status
