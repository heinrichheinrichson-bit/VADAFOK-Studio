# VADAFOK Studio – Project Roadmap / Skilltree

Stand: v2.6.2

Diese Datei dient als zentrale Projektübersicht. Sie soll im GitHub-Repository liegen und regelmäßig aktualisiert werden.

---

## Aktueller stabiler Stand

### Aktuelle Version

```text
v2.6.2 - Keyboard Editing
```

### Status

```text
Stabil / auf GitHub gesichert
```

---

# 1. Core Foundation

## Erledigt

- [x] Projektstruktur
- [x] Library-System
- [x] Bildimport
- [x] Banner Editor
- [x] Caption-Grundlagen
- [x] Template-System
- [x] Ordnerbasierte Templates
- [x] Template speichern/laden
- [x] Template löschen
- [x] Template umbenennen
- [x] Template duplizieren
- [x] Default Template
- [x] Card Creator nutzt neues Template-System
- [x] GitHub-Anbindung

## Offene technische Basis-Themen

- [ ] Saubere Versionsanzeige im UI
- [ ] About/Info-Fenster
- [ ] Settings/Preferences-Seite
- [ ] Backup/Restore für Projektdaten
- [ ] Export/Import kompletter Template-Pakete

---

# 2. Template Editor

## Erledigt

- [x] Felder erstellen
- [x] Felder löschen
- [x] Felder umbenennen
- [x] Felder verschieben
- [x] Felder skalieren
- [x] Eigenschaften speichern
- [x] Hintergrund aus Library setzen
- [x] Hintergrund aus Datei setzen
- [x] Flackerfreies Feldziehen
- [x] Keine doppelten/geisterhaften Felder
- [x] Copy Field
- [x] Zoom
- [x] Pan
- [x] Flackerfreies Pan
- [x] Smart Guides
- [x] Smart Snap
- [x] Multi Selection
- [x] Group Move
- [x] Multi Copy
- [x] Multi Delete
- [x] Alignment Tools
- [x] Distribute H/V
- [x] Keyboard Editing

## Aktuelle Editor-Steuerung

- `Ctrl + Klick` = mehrere Felder auswählen
- Pfeiltasten = 1 px bewegen
- `Shift + Pfeiltaste` = 10 px bewegen
- `Ctrl + D` = Auswahl duplizieren
- `Ctrl + A` = alle Felder auswählen
- `Delete / Backspace` = Auswahl löschen
- `Esc` = Auswahl aufheben
- Mittlere Maustaste / Shift + Drag = Pan
- Ctrl + Mausrad = Zoom

## Nächste mögliche Schritte

- [ ] Undo / Redo
- [ ] Verbesserte Distribution mit echten gleichen Abständen
- [ ] Lock / Unlock Fields
- [ ] Layer Panel
- [ ] Bring to Front / Send to Back
- [ ] Group / Ungroup
- [ ] Auswahlrahmen per Drag
- [ ] Mehrere Felder gemeinsam skalieren
- [ ] Feldrotation
- [ ] Snap-Toleranz einstellbar
- [ ] Smart Guides für Gruppenbox verbessern
- [ ] Text-Vorschau mit echten Beispieldaten
- [ ] WYSIWYG-Schriftgröße im Editor
- [ ] Textausrichtung links/zentriert/rechts
- [ ] Vertikale Textausrichtung
- [ ] Schatten / Glow / Stroke-Optionen
- [ ] Eigene Fonts
- [ ] Presets für Feldstyles

---

# 3. Card Creator

## Erledigt

- [x] Template auswählen
- [x] Card Preview
- [x] Richtiger Background pro Template
- [x] Hochformat-/Querformat-Support
- [x] Render PNG
- [x] Dynamische Felder aus Template
- [x] Card Creator nutzt ordnerbasiertes Template-System

## Nächste mögliche Schritte

- [ ] Export-Dateinamen verbessern
- [ ] Export-Ordner öffnen
- [ ] Render-Erfolgsmeldung verbessern
- [ ] Mehrere Cards nacheinander rendern
- [ ] Batch Rendering
- [ ] Presets für häufige Card-Inhalte
- [ ] Card-Daten speichern/laden
- [ ] Card History
- [ ] Transparenter Export optional
- [ ] Exportgröße auswählbar
- [ ] JPG/WebP Export zusätzlich zu PNG
- [ ] Live Preview beim Tippen verbessern
- [ ] Eingabefelder gruppieren
- [ ] Validierung leerer Felder

---

# 4. Banner Editor

## Erledigt

- [x] Banner-Bild laden
- [x] Textfeld bearbeiten
- [x] Textfeld verschieben
- [x] Reset Area
- [x] Reset Standardwerte
- [x] Flackerfreies Arbeiten
- [x] Speichern/Laden

## Auf Pause / Später

- [ ] Mehrere Textfelder im Banner Editor
- [ ] Banner Editor auf Template-Engine vereinheitlichen
- [ ] Banner Presets
- [ ] Banner Export-Varianten
- [ ] Banner direkt an OBS senden

---

# 5. Caption / Text Engine

## Erledigt

- [x] Caption-Grundlagen
- [x] Erste Layout-Logik

## Auf Pause / Später

- [ ] Caption Editor ausbauen
- [ ] Lauftexte
- [ ] Automatische Texteinpassung
- [ ] Caption Presets
- [ ] Captions aus Card-Daten generieren
- [ ] OBS Live Caption
- [ ] Timer / Countdown Captions

---

# 6. OBS Integration

## Teilweise vorhanden

- [x] OBS-Grundlagen / Controller-Struktur

## Noch offen

- [ ] OBS-Verbindung im UI prüfen
- [ ] Szene auswählen
- [ ] Quelle auswählen
- [ ] Card direkt an OBS senden
- [ ] Banner direkt an OBS senden
- [ ] Live Card aktualisieren
- [ ] Live Caption aktualisieren
- [ ] Automatische Szenenwechsel
- [ ] Statusanzeige Verbindung
- [ ] Fehlerbehandlung bei fehlender OBS-Verbindung

---

# 7. Live Tools

## Geplant

- [ ] Live Card
- [ ] Live Banner
- [ ] Live Caption
- [ ] Stream Schedule Live View
- [ ] Now Showing Live View
- [ ] Next Up Live View
- [ ] Event Card Live View
- [ ] Sponsor Card Live View
- [ ] Lower Thirds
- [ ] Credits / End Card
- [ ] Stream Starting Soon Cards
- [ ] Be Right Back Cards
- [ ] Intermission Cards

---

# 8. Template Packs / Content Types

## Geplant

- [ ] Streamplan
- [ ] Weekly Schedule
- [ ] Now Showing
- [ ] Next Stream
- [ ] Feature Presentation
- [ ] Movie Card
- [ ] Game Card
- [ ] Event Card
- [ ] Tournament Card
- [ ] Credits Card
- [ ] Sponsor Card
- [ ] Social Media Card
- [ ] Announcement Card
- [ ] News Card
- [ ] Lower Third
- [ ] Scoreboard

---

# 9. Professional Editor Features

## Geplant

- [ ] Undo / Redo
- [ ] History Stack
- [ ] Layer Panel
- [ ] Lock Fields
- [ ] Hide Fields
- [ ] Group / Ungroup
- [ ] Duplicate with Offset
- [ ] Paste in Place
- [ ] Copy/Paste zwischen Templates
- [ ] Field Style Presets
- [ ] Style Copy / Paste Style
- [ ] Rulers
- [ ] Manual Guides
- [ ] Guide Manager
- [ ] Measurement Display
- [ ] Equal Spacing / Gap Distribution
- [ ] Object Snapping
- [ ] Boundary Snapping
- [ ] Keyboard Shortcut Overview

---

# 10. Data / Project Management

## Geplant

- [ ] Projektdatei
- [ ] Template-Bibliothek exportieren
- [ ] Template-Bibliothek importieren
- [ ] Automatische Backups
- [ ] Versionierte Template-Daten
- [ ] Migration alter Daten
- [ ] Aufräumen ungenutzter Bilder
- [ ] Template-Pakete teilen
- [ ] Beispielpaket mit Demo-Templates

---

# 11. UI / UX Polish

## Erledigt

- [x] Dunkles VADAFOK-Design
- [x] Besserer Rename-Dialog
- [x] Kompaktere Template-Verwaltung
- [x] Smart Guides visuell integriert

## Geplant

- [ ] Einheitliche Icons
- [ ] Tooltips
- [ ] Shortcut-Hinweise
- [ ] Statusbar verbessern
- [ ] Bessere Fehlermeldungen
- [ ] Fortschrittsanzeigen
- [ ] Schnellzugriff-Leiste
- [ ] Vollbild-Editor-Modus
- [ ] Panels ein-/ausklappen
- [ ] Layout speichern
- [ ] Theme-Einstellungen

---

# 12. Pausierte / Verworfene Ansätze

## Verworfene Zwischenstände

Diese Versionen waren Entwicklungsversuche und sollten nicht als Basis genutzt werden:

- 2.2.2
- 2.2.3
- 2.2.4
- 2.3.1
- 2.3.2
- 2.3.3
- 2.3.4
- 2.4.4-debug
- 2.4.4-debug2
- 2.4.8-debug
- 2.5.0-debug
- 2.5.1-debug
- 2.5.2-debug
- 2.5.8 Grid/Snap Ansatz

## Grund

Diese Versionen waren wichtig zur Fehlersuche, aber nicht stabil oder wurden durch bessere Lösungen ersetzt.

---

# 13. Aktuelle Prioritäten

## Kurzfristig

1. Undo / Redo
2. Echte Equal-Spacing-Distribution
3. Lock / Unlock Fields
4. Layer Panel
5. Copy/Paste zwischen Templates

## Mittelfristig

1. Card Creator Export verbessern
2. Live Card bauen
3. OBS-Anbindung ausbauen
4. Template Packs erstellen
5. WYSIWYG-Schriftvorschau verbessern

## Langfristig

1. Vollwertiger Stream-Grafik-Editor
2. Live-OBS-Steuerung
3. Template-Marktplatz / Template-Packs
4. Komplettes VADAFOK Studio 3.0

---

# 14. Versionshistorie

## v2.3.5

- Stabiler Template Editor
- Flackerfreies Ziehen
- Keine doppelten Felder
- Library/Background wieder stabil

## v2.4.x

- Template-Verwaltung
- Rename
- Duplicate
- Delete
- Default
- Card Creator Bugfixes

## v2.5.x

- Card Creator auf neues Template-System umgestellt
- Copy Field
- Zoom
- Pan
- Smart Guides
- Smart Snap
- Multi Selection

## v2.6.x

- Group Move
- Multi Copy
- Alignment Tools
- Keyboard Editing

---

# 15. Nächster empfohlener Schritt

```text
v2.6.3 - Undo / Redo
```

Warum:

Jetzt, wo der Editor viele Bearbeitungsfunktionen hat, wird Undo/Redo wichtig, damit man risikofrei experimentieren kann.

