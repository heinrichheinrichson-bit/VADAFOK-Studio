# VADAFOK Studio – Project Rules

Stand: 2.19 RC1

Dieses Dokument ergänzt die vorhandenen Entwicklungsregeln. Historische Roadmaps, Ideas- und Entwicklungsdokumente werden nicht überschrieben oder stillschweigend entfernt.

## 1. Produktprinzipien

- VADAFOK Studio unterstützt einen stummen Stream: Die Stimme ist eine private Eingabemethode, nicht Teil des öffentlichen Audios.
- Workflow vor Funktionsmenge: Neue Funktionen müssen im echten Stream Zeit, Klicks oder Unsicherheit reduzieren.
- OBS wird ergänzt, nicht ersetzt.
- Stable Funktionen werden nur bei einem belegten praktischen Bedarf umgebaut.
- VADAFOK bleibt ohne Cloud, KI und Sprachsteuerung grundsätzlich benutzbar.

## 2. Entwicklung

- Eine Version verfolgt ein klar abgegrenztes Hauptziel.
- Neue Funktionen beginnen als RC und werden erst nach einem dokumentierten Test als stabil gespeichert.
- Grundlage ist immer der zuletzt erfolgreich getestete und auf GitHub gespeicherte Stand.
- Fehlerkorrekturen sollen den kleinstmöglichen Codebereich verändern.
- Kein „nebenbei“-Refactoring in Feature-Releases.
- Cleanup, Architekturumbau und neue Features werden möglichst getrennt durchgeführt.

## 3. Dokumentation und Historie

- `ROADMAP`, `MASTER_ROADMAP` und `IDEAS` werden ergänzt, niemals durch verkürzte Neufassungen ersetzt.
- Erledigte Ideen bleiben als erledigt dokumentiert, statt zu verschwinden.
- Historisch wichtige RC- und Testunterlagen werden archiviert.
- Reine temporäre Testanleitungen dürfen erst nach einer Bestandsaufnahme entfernt werden.
- Jede Löschung im Cleanup muss in einem Cleanup-Protokoll begründet werden.

## 4. UI und Fenster

- Fenster dürfen sich ihre letzte Größe und Position merken.
- Benutzerentscheidungen über Fenstergröße haben Vorrang; keine unnötigen Mindestgrößen erzwingen.
- Kontextabhängige Sprachhilfe zeigt nur Befehle, die im geöffneten Fenster tatsächlich anwendbar sind.
- Gleiche Aktionen haben projektweit dieselbe Bedeutung:
  - `Show` = anzeigen/senden
  - `Reset` = Inhalt bewusst leeren
  - `Stop` = aktuellen Vorgang abbrechen
  - `Back` = zum vorherigen Kontext zurückkehren
- Keine blockierenden Fenster ohne funktionierendes X, Escape und sicheren Rückweg.

## 5. Voice Control

- Mikrofon-Audio wird niemals automatisch an OBS übertragen.
- Windows Speech ist für feste Befehle vorgesehen; Whisper für Diktat.
- Befehlsphrasen dürfen nie als sichtbarer Caption-Text übernommen werden.
- Texte werden vor dem Senden kontrollierbar angezeigt.
- Quick Cards bleiben vollständige, häufig verwendete Kommentare und Antworten.
- Voice Library und Recognition-Aliase bleiben getrennt von der Quick-Card-Datenquelle.

## 6. Daten und Assets

- Benutzerdaten und automatisch erzeugte Zustände werden getrennt von Programmcode gespeichert.
- Bibliotheken werden nicht ungefragt automatisch umgeschrieben.
- Generierte Exporte und Vorschauen sollen nicht automatisch versioniert werden, sofern sie keine bewusst gepflegten Beispiel-Assets sind.
- Vor dem Entfernen oder Verschieben einer Datei wird geprüft, ob sie im Code, in Batch-Dateien oder in Dokumentation referenziert wird.

## 7. Release- und Git-Regeln

- Vor Installation eines Overlay-Pakets: `git status` prüfen.
- Nach bestandenem Test: Änderungen gemeinsam mit passendem Versions-Commit speichern.
- Fehlgeschlagene RCs werden nicht committed.
- Jede Testanleitung enthält Ausgangsversion, Installation, Tests, Rollback und Commit-Hinweis.
