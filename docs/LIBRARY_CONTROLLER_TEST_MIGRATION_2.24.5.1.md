# VADAFOK Studio 2.24.5.1 – Library Controller Test Suite Migration

Vier ältere Picker-Tests prüften weiterhin die vor dem Refactoring verwendete
Architektur direkt in `app.py`.

Migriert wurden:

- `test_explicit_template_picker_return.py`
- `test_picker_mode_persistence.py`
- `test_template_background_one_click.py`
- `test_template_background_picker.py`

Die Tests prüfen jetzt:

- Delegation aus `app.py`;
- Picker-Zustand im `LibraryController`;
- Rückkehr zum Template Editor über den Controller;
- einfacher Klick bleibt Auswahl/Vorschau;
- Doppelklick nutzt weiterhin die Standardaktion;
- normaler Library-Betrieb bleibt möglich.

Programmcode wird nicht verändert.
