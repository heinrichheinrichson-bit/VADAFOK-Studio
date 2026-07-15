# VADAFOK Studio 2.16.6 – Hybrid Voice Quick Caption

## Install over

The currently tested local state:

- VADAFOK Studio 2.16.5.1
- Voice TEST 01 through TEST 08 installed

This is a release-finalization overlay. Do not apply it directly to a clean 2.16.5.1 checkout.

## Installation

1. Close VADAFOK Studio.
2. Copy this ZIP's complete contents into the VADAFOK Studio project folder.
3. Confirm replacement of existing files.
4. Run `INSTALL_VOICE_DEPENDENCIES.bat` if the dependencies are not already installed.
5. Run `FINALIZE_RELEASE_2.16.6.bat` once. It appends documentation and removes obsolete TEST files.
6. Start VADAFOK Studio normally.

## Rollback before commit

Close VADAFOK Studio and run in Git Bash:

```bash
git restore .
git clean -fd
```

Warning: `git clean -fd` removes all untracked files and folders in the repository.

## Release test

1. Confirm `2.16.6` in both the window title and sidebar.
2. Confirm normal navigation and manual F8 Quick Caption still work.
3. Test `de-DE`: `Live Card`, German sentence, `Vadafok Show`.
4. Test `en-US`: `Live Card`, English sentence, `Vadafok Show`.
5. Test `Vadafok Reset` and `Vadafok Stop`.
6. Confirm no command text appears in the banner.
7. Confirm OBS receives only the reviewed caption text.
8. Restart the application once and repeat one German and one English caption.

Do not commit if any of these checks fail.
