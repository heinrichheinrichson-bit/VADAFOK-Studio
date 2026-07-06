# Architecture

## v2.8.3 Export Engine

New module:

```text
vadafok_studio/core/export_engine.py
```

Responsibilities:
- list built-in profiles
- resolve profile metadata
- build output paths
- resize/canvas images for profile output
- save PNG/JPEG with profile settings

Card Creator workflow:
1. render normal template card to temporary PNG
2. load image
3. apply selected export profile
4. save final output
