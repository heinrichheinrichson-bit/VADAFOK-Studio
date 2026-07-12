# CHANGELOG

## v2.16.3 - Live Card Style Cleanup

### Verified
- The old Style dropdown only changed and saved a variable.
- It was not used by preview rendering, smart PNG rendering or OBS display.
- It therefore had no visible effect.

### Changed
- Removed the ineffective Style dropdown from Live Card.
- Engine and Duration now use the available space more clearly.
- Added CURRENT BANNER with the real filename beneath the preview.
- Preview status now displays the actual banner filename.
- Added RESET TEXT beside REFRESH PREVIEW.
- CHANGE BANNER remains the primary banner-selection action.

### RESET TEXT
- Restores `CHAT WAS RIGHT.`
- Refreshes the preview immediately.
- Does not send anything to OBS.

### Preserved
- CHANGE BANNER workflow.
- Automatic return from Library to Live Card.
- SHOW, HIDE, CLEAR and SAVE QUICK.
- Caption Engine and smart PNG rendering.
