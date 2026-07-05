# Architecture

## v2.7.0 Group Foundation

Fields now receive stable IDs:

```json
{
  "id": "uuid",
  "name": "title"
}
```

Groups reference fields by stable ID:

```json
{
  "id": "uuid",
  "name": "Group",
  "field_ids": ["field-uuid-1", "field-uuid-2"]
}
```

This is more robust than index-based grouping.
