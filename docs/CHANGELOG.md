# CHANGELOG

## v2.8.1.1 - Fix Style Engine import

### Fixed
- `style_engine` import was missing in `app.py`.
- Style Preset saving no longer fails with `name 'style_engine' is not defined`.
- Save Style now asks before overwriting an existing style name.

### Kept
- Card Creator `UNDO DATA`.
- Card Creator `REDO DATA`.
- `CLEAR FIELDS` undo support.

## v2.8.1 - Finalize Style Save and add Card Creator data undo
- Added style save verification and Card Creator data undo/redo.
