# CHANGELOG

## v2.13.0.1 - Silent Director RUN Fix

### Fixed
- RUN / RUN PRESET no longer accesses destroyed Live Card text widgets.
- Empty presets now show a clear info message instead of appearing to do nothing.
- Scene switching from Silent Director uses the OBS controller directly.

### Safety
- Banner execution from Silent Director is temporarily queued/logged only.
- Engine-level banner execution returns in v2.13.1 with a proper Preset Editor path.
