# CHANGELOG

## v2.10.3.4 - Connect Probe Variable Fix

### Fixed
- Fixed `connected_after_probe` error after CONNECT.
- CONNECT now initializes probe state safely.
- OBS status probe behavior from v2.10.3.3 remains active.

### Kept
- REFRESH detects manually closed OBS.
- SHOW/HIDE check real OBS connection before sending.
- DISCONNECT hard reset remains included.
