"""
Isolated canvas layer helpers for Template Editor.

This module is intentionally additive. It does not replace Library,
Template Store, Card Creator, or background assignment logic.

Goal:
- Keep background items untouched during drag.
- Delete only overlay items by a dedicated tag.
"""

OVERLAY_TAG = "template_field_overlay"


def clear_overlay(canvas):
    try:
        canvas.delete(OVERLAY_TAG)
    except Exception:
        pass


def tag_overlay(kwargs=None):
    kwargs = dict(kwargs or {})
    tags = kwargs.get("tags", ())
    if isinstance(tags, str):
        tags = (tags,)
    kwargs["tags"] = tuple(tags) + (OVERLAY_TAG,)
    return kwargs
