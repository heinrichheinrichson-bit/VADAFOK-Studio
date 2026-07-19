VADAFOK STUDIO 2.27.0.4
========================

INHALT
------
- Funktionierende DeepL-Free-Übersetzung aus 2.27.0.3
- Sicher validierte TLS-Zertifikate über certifi
- Zentraler Translation Runtime Service mit Cache und Log
- Neuer bevorzugter Sprachbefehl: VADAFOK ENGLISH
- VADAFOK TRANSLATE bleibt als Alias erhalten
- Zusätzliche Aussprachevarianten für ENGLISH / ENGLISCH
- Versionsnummer zentral auf 2.27.0.4 aktualisiert

INSTALLATION
------------
1. VADAFOK Studio schließen.
2. ZIP direkt nach
   F:\Vadafok Studio\VADAFOK_Studio
   entpacken.
3. Vorhandene Dateien ersetzen.
4. INSTALL_CERTIFICATES_2.27.0.4.bat doppelt anklicken.
5. VADAFOK über Start VADAFOK Studio.bat starten.

TEST
----
1. Sage: VADAFOK QUICK CARD
2. Sage: Das war knapp.
3. Warte, bis "That was close." angezeigt wird.
4. Sage: VADAFOK ENGLISH
5. Prüfe, ob "That was close." im Quick-Caption-Textfeld steht.
6. Sage: VADAFOK SHOW

WEITERE AKZEPTIERTE BEFEHLE
---------------------------
- VADAFOK ENGLISCH
- VADAFOK ENGLISH TEXT
- VADAFOK TRANSLATE
- VADAFOK TRANSLATION
- verschiedene Wake-Word-Varianten wie WADAFOK und VADA FOX

ROLLBACK MIT GIT BASH
---------------------
git restore vadafok_studio/version.py
git restore vadafok_studio/voice_control/foundation.py
git restore vadafok_studio/voice_control/quick_card_voice.py
git restore vadafok_studio/voice_control/voice_library.json
git restore vadafok_studio/translator
rm -f tests/test_translation_runtime.py
rm -f tests/test_deepl_ssl.py
rm -f INSTALL_CERTIFICATES_2.27.0.4.bat
rm -f requirements_translation.txt

Danach:
git status

LOG
---
Technische Übersetzungsdetails:
logs\translation.log
