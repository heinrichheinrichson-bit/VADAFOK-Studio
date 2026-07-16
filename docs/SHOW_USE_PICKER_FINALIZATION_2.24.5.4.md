# VADAFOK Studio 2.24.5.4 – SHOW / USE Picker Finalization

Der verlässlich unterstützte Ablauf ist:

1. Template-Bild einmal anklicken;
2. große Vorschau prüfen;
3. `SHOW / USE` drücken;
4. Hintergrund wird übernommen;
5. Template Editor öffnet sich automatisch.

Der Doppelklick wird nicht mehr als zugesicherter Picker-Ablauf dokumentiert,
weil die Library-Auswahl nach einem Klick das Thumbnail-Raster neu zeichnet.
Dadurch wird das ursprüngliche Widget ersetzt, bevor Tkinter den zweiten Klick
zuverlässig als Doppelklick erkennen kann.

Der funktionierende `SHOW / USE`-Pfad bleibt unverändert.
