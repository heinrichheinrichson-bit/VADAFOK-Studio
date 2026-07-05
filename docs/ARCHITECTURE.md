# Architecture

## v2.6.6 Notes

Field data can now contain:

```json
{
  "locked": true,
  "hidden": false
}
```

## Rendering Rule
Hidden fields are skipped during card rendering.

## Editor Rule
Hidden fields are skipped by:
- overlay drawing
- canvas hit testing
- smart guide targets
- selection-based operations
