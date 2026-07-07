# CHANGELOG

## v2.11.5 - Recursive OBS Scene Scanner

### Added
- Recursive source scanner in OBSController:
  - reads normal scene items
  - attempts to read group contents
  - includes nested/group sources for Overlay Health
- Overlay Health now uses recursive source scan when available.

### Improved
- Overlay Health can detect VADAFOK sources inside OBS groups.
- Debug log now shows `Overlay Recursive Found`.

### Notes
- This is still diagnosis only.
- Automatic overlay installation is not included yet.
