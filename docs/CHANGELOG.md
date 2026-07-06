# CHANGELOG

## v2.8.6 - Add Batch Projects clean integration

### Added
- `batch_projects/` folder.
- Save Batch Project as `.vbatch`.
- Load Batch Project from `.vbatch`.
- SAVE PROJECT button.
- LOAD PROJECT button.
- Batch Project stores:
  - template
  - output name
  - export profile
  - field values

### Fixed / Design
- App UI does not use `Path` directly for Batch Project save/load.
- File logic lives in `batch_engine.py`.
- SAVE/LOAD dialogs start in `batch_projects/`.

## v2.8.5.2 - CSV / Excel Import stable
- CSV/XLSX import creates Batch Cards.
