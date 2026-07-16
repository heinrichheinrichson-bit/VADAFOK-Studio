# VADAFOK Studio 2.24.2 – Foundation – Template Editor Controller

Erster kontrollierter Schritt zur Auslagerung des Template Editors.

Aus `app.py` ausgelagert:

- Prüfung, ob ein Template existiert;
- Zurücksetzen von Auswahl und Gruppenstatus;
- Laden des gewählten Templates;
- Anstoßen des bestehenden Template-Editor-Seitenaufbaus.

Bewusst noch nicht ausgelagert:

- Canvas;
- Dragging;
- Smart Guides;
- Feldbearbeitung;
- Rendering;
- Speichern;
- Undo/Redo.

Dadurch bleibt die Änderung klein und risikoarm.
