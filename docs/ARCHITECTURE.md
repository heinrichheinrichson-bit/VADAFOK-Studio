# Architecture

## v2.7.6.1 Drop Indicator

Layer Drag & Drop now uses a temporary UI frame as a drop indicator.

State:
- template_layer_drop_indicator
- template_layer_drop_target

The indicator is a visual-only Layer Panel element and does not affect template data until mouse release.
