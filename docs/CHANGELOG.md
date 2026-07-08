# CHANGELOG

## v2.12.3 - Overlay Installer

### Added
- INSTALL SELECTED is now active.
- Installer uses selected Source Scene as overlay template.
- Installer adds only missing configured VADAFOK sources to selected target scenes.
- Existing sources are not deleted, overwritten, or duplicated.
- Per-scene install summary is written to the workflow log.
- Overlay Health is rescanned after installation.

### Safety
- Confirmation dialog before modifying OBS scenes.
- Scene-by-scene error handling.
- Only configured VADAFOK overlay source names are installed.
