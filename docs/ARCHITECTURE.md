# Architecture

## v2.8.5 Batch Engine

New module:

```text
vadafok_studio/core/batch_engine.py
```

Responsibilities:
- read CSV
- read XLSX
- normalize column and field names
- convert table rows to Batch Card items

Mapping rule:
- Column names are normalized.
- Template field names are normalized.
- Matching names are assigned automatically.

Example:
- column `Game`
- field `game`
- match

Batch item output:

```json
{
  "template": "Template Name",
  "output_name": "spieler_001",
  "profile": "Broadcast PNG",
  "values": {
    "game": "Finale"
  }
}
```
