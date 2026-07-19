VADAFOK STUDIO – TRANSLATION FOUNDATION 2.27.0.3
=================================================

Diese ZIP wird direkt über den VADAFOK_Studio-Projektordner entpackt.
Vorhandene Dateien müssen ersetzt werden.

WAS DIE VERSION ÄNDERT
----------------------
- DeepL API Free wird weiterhin automatisch an einem API-Key mit :fx erkannt.
- TLS/SSL-Zertifikate werden sicher über certifi geprüft.
- Die Zertifikatsprüfung wird NICHT abgeschaltet.
- Ein zentraler Translation Runtime Service wird hinzugefügt.
- Übersetzungen werden im Speicher zwischengespeichert.
- Technische Fehler landen in logs/translation.log.
- Das Quick-Card-Fenster zeigt nur noch eine verständliche Fehlermeldung.
- Der bestehende Sprachablauf bleibt:
  VADAFOK ONE/TWO/THREE, VADAFOK TEXT, VADAFOK TRANSLATE, VADAFOK SHOW.

GENAUE INSTALLATION
-------------------
1. VADAFOK Studio schließen.
2. Diese ZIP direkt nach
   F:\Vadafok Studio\VADAFOK_Studio
   entpacken.
3. Bei der Windows-Frage vorhandene Dateien ERSETZEN.
4. Im Projektordner die Datei
   INSTALL_CERTIFICATES_2.27.0.3.bat
   doppelt anklicken.
5. Warten, bis "OK" angezeigt wird.
6. VADAFOK Studio normal über "Start VADAFOK Studio.bat" starten.
7. Test:
   - VADAFOK QUICK CARD
   - "Das war knapp."
   - Im Vorschlagsfenster muss "That was close." erscheinen.
   - VADAFOK TRANSLATE
   - VADAFOK SHOW

DEEPL-KEY PRÜFEN
----------------
In Git Bash:
py -c "import os; print(bool(os.environ.get('DEEPL_API_KEY')))"

Die Ausgabe muss True sein.

ROLLBACK MIT GIT BASH
---------------------
git restore vadafok_studio/translator
git restore vadafok_studio/voice_control/quick_card_voice.py
rm -f tests/test_translation_runtime.py
rm -f tests/test_deepl_ssl.py
rm -f INSTALL_CERTIFICATES_2.27.0.3.bat
rm -f requirements_translation.txt

Danach:
git status

HINWEIS ZUR SICHTBAREN VERSIONSNUMMER
-------------------------------------
Die Datei vadafok_studio/version.py wurde nicht bereitgestellt und wird deshalb
in diesem Patch bewusst nicht verändert. Die bestehende Nummer im Fenstertitel
bleibt unverändert. Für die offizielle Versionsanzeige bitte version.py hochladen.
