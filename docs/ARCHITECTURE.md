# Architecture

## v2.7.1 Group Management

Groups are first-class layer objects:

```json
{
  "id": "uuid",
  "name": "Intro Card",
  "field_ids": ["field-id-1", "field-id-2"],
  "locked": false,
  "hidden": false
}
```

Group lock/hide currently propagates to all member fields.

Future:
- collapsible group tree
- nested groups
- group colors
