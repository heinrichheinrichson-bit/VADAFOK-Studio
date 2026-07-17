# Template Selection & History Refresh Audit – 2.25.0.4

Selection changes no longer destroy and recreate the complete Layers panel. The existing field and group buttons are retained and only their selection-dependent text and colors are updated.

This partial path is used for Layers clicks, canvas clicks, locked-field selection, marquee selection, and clearing a marquee selection. Structural changes and Undo/Redo continue to use the safe full rebuild path because field order, names, groups, visibility, or locks may have changed.

The user-facing selection, multi-selection, drag, Smart Snap, Smart Guides, Undo, and Redo behavior is unchanged.
