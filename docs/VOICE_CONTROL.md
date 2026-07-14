# VADAFOK Studio Voice Control

## Purpose

VADAFOK Studio remains a silent-stream application. The microphone is used locally as an input device so the streamer can create visible banners and intertitles without speaking to the audience.

## Release 2.16.6 architecture

- **Windows System.Speech:** fixed command recognition.
- **faster-whisper:** local German and English free-text dictation.
- **Voice Matcher:** optional correction against the separate Voice Library and existing Quick Card sentences.
- **Quick Caption:** final review and editing before output.
- **Existing SHOW path:** sends the approved caption through the application's established OBS workflow.

No microphone audio is intentionally routed to OBS by this module.

## Commands

The fixed commands are the same in German and English recognition modes:

- `Live Card` – open Quick Caption and begin dictation.
- `Vadafok Show` – send the current caption.
- `Vadafok Reset` – clear the current caption text.
- `Vadafok Stop` – close Quick Caption without sending.

## Dictation languages

- Select `de-DE` for German dictation.
- Select `en-US` for English dictation.
- Windows Speech handles the fixed commands; Whisper handles the free caption text.

## Voice Library and Quick Cards

`voice_library.json` is a dedicated recognition aid containing prepared phrases and aliases. Quick Cards remain a separate user-facing collection of frequently used complete comments and responses.

The matcher may read Quick Card sentences as an additional comparison source. It does not edit, expand, or restructure the Quick Card library.

## Safety behavior

- Commands beginning with the Vadafok wake word are blocked from the visible caption.
- A caption is not sent automatically after dictation.
- The user can inspect and edit the text before saying `Vadafok Show`.
- `Vadafok Stop` closes the window without sending.

## Dependencies

Install the local dictation dependencies once with:

`INSTALL_VOICE_DEPENDENCIES.bat`

The first use downloads the selected Whisper model. Later starts use the locally cached model.

## Known limitations

- Speech recognition is not infallible; the text field remains the final review step.
- A quiet environment and a well-positioned microphone improve results.
- Very short phrases may be harder to distinguish than full sentences.
- Model loading and transcription speed depend on the computer.

## Planned extensions

- Voice selection of existing Quick Cards.
- User-editable commands and wake word.
- Voice Library editor.
- Optional correction learning from user edits.
- Additional voice-controlled silent-stream modules.
