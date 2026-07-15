## 2.16.7 RC1 – Voice Language Selection

- Replaced the editable Windows Speech culture field with a controlled dropdown.
- Available command-recognizer cultures: `de-DE` and `en-US`.
- Whisper dictation remains multilingual and continues to auto-detect German and English.
- The selected culture applies to the Windows command recognizer (`Live Card`, `Vadafok Show`, `Vadafok Reset`, `Vadafok Stop`).
- Invalid values such as `en-EN` can no longer be entered through the Settings UI.
- Existing Save Settings and Restart Listener actions remain the authoritative workflow.
