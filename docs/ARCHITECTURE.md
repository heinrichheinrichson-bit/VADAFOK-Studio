# Architecture

## v2.8.6 Batch Projects

Batch Project file logic is in:

```text
vadafok_studio/core/batch_engine.py
```

The UI passes string paths to the engine.
The app UI does not need to construct `Path(...)` for save/load.

Batch Projects use `.vbatch` files in the `batch_projects/` folder.

Internal JSON format:

```json
{
  "format": "VADAFOK_BATCH_PROJECT",
  "version": 1,
  "items": [
    {
      "template": "Template Name",
      "output_name": "card_001",
      "profile": "Broadcast PNG",
      "values": {
        "date": "2026-07-06"
      }
    }
  ]
}
```
