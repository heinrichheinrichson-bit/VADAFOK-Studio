from pathlib import Path
import json
import shutil
import re

from .config import TEMPLATE_LIBRARY_DIR


def _safe_slug(name: str) -> str:
    name = (name or "Template").strip()
    slug = re.sub(r"[^A-Za-z0-9ÄÖÜäöüß _-]+", "", name).strip().replace(" ", "_")
    return slug or "Template"


def ensure_template_root():
    TEMPLATE_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)


def template_dir(name: str) -> Path:
    ensure_template_root()
    return TEMPLATE_LIBRARY_DIR / _safe_slug(name)


def template_json_path(name: str) -> Path:
    return template_dir(name) / "template.json"


def list_templates():
    ensure_template_root()
    names = []
    for p in sorted(TEMPLATE_LIBRARY_DIR.iterdir()):
        if p.is_dir() and (p / "template.json").exists():
            try:
                data = load_template(p.name)
                names.append(data.get("name", p.name))
            except Exception:
                names.append(p.name)
    return names


def default_template(name="New Template"):
    return {
        "name": name,
        "background": "background.png",
        "fields": [
            {
                "name": "date",
                "x": 120,
                "y": 80,
                "width": 420,
                "height": 90,
                "font_family": "Bebas Neue",
                "font_size": 90,
                "text_color": "#FFFFFF",
                "stroke_color": "#000000",
                "stroke_width": 3,
                "uppercase": True,
            },
            {
                "name": "game",
                "x": 120,
                "y": 190,
                "width": 900,
                "height": 120,
                "font_family": "Bebas Neue",
                "font_size": 110,
                "text_color": "#FFFFFF",
                "stroke_color": "#000000",
                "stroke_width": 3,
                "uppercase": True,
            },
            {
                "name": "time",
                "x": 120,
                "y": 340,
                "width": 360,
                "height": 90,
                "font_family": "Bebas Neue",
                "font_size": 90,
                "text_color": "#FFFFFF",
                "stroke_color": "#000000",
                "stroke_width": 3,
                "uppercase": True,
            },
        ],
    }


def create_template(name="New Template"):
    ensure_template_root()
    base = name
    final_name = base
    index = 1
    while template_json_path(final_name).exists():
        index += 1
        final_name = f"{base} {index}"
    d = template_dir(final_name)
    d.mkdir(parents=True, exist_ok=True)
    data = default_template(final_name)
    save_template(final_name, data)
    return data


def load_template(name: str):
    p = template_json_path(name)
    if not p.exists():
        data = create_template(name)
        return data
    return json.loads(p.read_text(encoding="utf-8"))


def save_template(name: str, data: dict):
    d = template_dir(name)
    d.mkdir(parents=True, exist_ok=True)
    data = dict(data)
    data["name"] = name
    (d / "template.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data


def background_path(name: str, data: dict | None = None):
    data = data or load_template(name)
    bg = data.get("background", "background.png")
    p = Path(bg)
    if p.is_absolute():
        return p
    return template_dir(name) / bg


def set_background_from_file(name: str, source_path: str):
    data = load_template(name)
    d = template_dir(name)
    d.mkdir(parents=True, exist_ok=True)

    src = Path(source_path)
    if not src.exists():
        raise FileNotFoundError(str(src))

    suffix = src.suffix.lower() or ".png"
    dest = d / f"background{suffix}"
    shutil.copy2(src, dest)

    data["background"] = dest.name
    save_template(name, data)
    return data, dest


def import_legacy_templates(legacy_profiles: dict):
    """
    Optional migration from old template_profiles.json.
    Does not delete old data.
    """
    ensure_template_root()
    imported = []
    for name, data in (legacy_profiles or {}).items():
        if not isinstance(data, dict):
            continue
        if template_json_path(name).exists():
            continue
        new_data = default_template(name)
        new_data.update(data)
        # If old background was absolute, copy it into the template folder if possible.
        old_bg = data.get("background", "")
        if old_bg and Path(old_bg).exists():
            try:
                save_template(name, new_data)
                set_background_from_file(name, old_bg)
            except Exception:
                save_template(name, new_data)
        else:
            save_template(name, new_data)
        imported.append(name)
    return imported
