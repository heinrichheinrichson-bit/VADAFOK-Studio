# Architecture

## v2.8.4 Batch Cards Phase 1

Batch item structure:

```json
{
  "template": "Template Name",
  "output_name": "card_name",
  "profile": "Broadcast PNG",
  "values": {
    "title": "Example"
  }
}
```

Batch Cards are currently in-memory only.

Flow:
1. Add Current stores current form data and export settings.
2. Selecting an item restores its values.
3. Render Batch iterates items, restores each state, and renders final output.

Future:
- CSV import creates batch items.
- Excel import creates batch items.
- Batch progress bar.
- Saved batch projects.
