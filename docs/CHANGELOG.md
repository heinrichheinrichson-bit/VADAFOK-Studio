# CHANGELOG

## v2.7.0 - Add stable Group / Ungroup foundation

### Added
- Stable field IDs for template fields.
- Group / Ungroup controls in Template Editor.
- Groups are stored with stable field IDs instead of field indices.
- Groups appear in the Layer Panel with `📦`.
- Clicking a group selects its visible fields.
- Copying a complete group creates a copied group.

### Changed
- Layer Panel shows group membership next to grouped fields.
- Group data is more robust against layer reordering.
- Hidden fields are ignored when selecting a group from the Layer Panel.

### Testing
- To be verified before Git release.

## v2.6.6 - Add hide and show fields
- Added visibility toggle in Layers panel.
- Hidden fields are skipped in editor and rendering.
