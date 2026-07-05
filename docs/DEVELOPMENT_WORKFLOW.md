# Development Workflow

## Release States

- Stable: tested and committed.
- Test: currently being tested.
- Rejected: failed testing and must not be used as base.

## Current Example

- v2.7.6.1 = Stable
- v2.7.7 = Rejected
- v2.7.7.1 = Rejected
- v2.7.7.2 = Rejected
- v2.7.7.3 = Test
- v2.7.7.4 = Test

## Before Installing a Test Version

1. Close VADAFOK Studio.
2. Make a backup of the current project folder.
3. Extract the new ZIP.
4. Copy contents into the project folder and overwrite.
5. Start with `Start VADAFOK Studio.bat`.
6. Test using `docs/RELEASE_CHECKLIST.md`.

## Git Rule

Only commit after all tests passed.
