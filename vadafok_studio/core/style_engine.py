from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List


STYLE_KEYS = [
    "font_family",
    "font_size",
    "text_color",
    "stroke_color",
    "stroke_width",
    "uppercase",
    "align",
    "valign",
    "bold",
    "italic",
    "underline",
    "shadow",
    "shadow_color",
    "shadow_x",
    "shadow_y",
    "background_color",
    "border_color",
    "border_width",
    "opacity",
]


def project_root() -> Path:
    # style_engine.py lives in:
    # <project>/vadafok_studio/core/style_engine.py
    # parents[2] is the visible project folder containing styles/
    return Path(__file__).resolve().parents[2]


def styles_dir() -> Path:
    path = project_root() / "styles"
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())
    safe = safe.strip("_")
    return safe or "style"


def style_path(name: str) -> Path:
    return styles_dir() / f"{slugify(name)}.json"


def extract_style(field: Dict[str, Any]) -> Dict[str, Any]:
    # Save only visual properties. Even if a template field has few keys,
    # this still writes a valid JSON file.
    return {key: field[key] for key in STYLE_KEYS if key in field}


def apply_style(field: Dict[str, Any], style: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in style.items():
        if key in STYLE_KEYS:
            field[key] = value
    return field


def restore_style(field: Dict[str, Any], style: Dict[str, Any]) -> Dict[str, Any]:
    """Replace every visual property while preserving field data and layout."""
    for key in STYLE_KEYS:
        field.pop(key, None)
    return apply_style(field, style)


def save_style(name: str, field: Dict[str, Any]) -> Path:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Style name is empty")

    path = style_path(clean_name)
    data = {
        "name": clean_name,
        "style": extract_style(field),
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    if not path.exists():
        raise OSError(f"Style file was not created: {path}")

    return path


def load_style(name: str) -> Dict[str, Any]:
    path = style_path(name)
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("style", {})


def delete_style(name: str) -> None:
    path = style_path(name)
    if path.exists():
        path.unlink()


def list_styles() -> List[str]:
    result = []
    folder = styles_dir()
    for path in sorted(folder.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            result.append(data.get("name") or path.stem)
        except Exception:
            result.append(path.stem)
    return result
