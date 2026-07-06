# Architecture

## v2.8.1

### Style Engine
Style saving now verifies that the target JSON file exists after writing.

### Card Creator Data History
Card Creator has lightweight data undo/redo:

- `card_data_undo_stack`
- `card_data_redo_stack`
- `card_push_data_history`
- `card_undo_data`
- `card_redo_data`

Currently this is focused on form data operations, especially `CLEAR FIELDS`.
