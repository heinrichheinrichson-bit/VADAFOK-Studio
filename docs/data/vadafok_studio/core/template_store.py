from pathlib import Path
import json
import shutil
import re

from .config import TEMPLATE_LIBRARY_DIR
MIGRATION_MARKER = TEMPLATE_LIBRARY_DIR / ".legacy_import_done"
DELETED_TEMPLATES_PATH = TEMPLATE_LIBRARY_DIR / ".deleted_templates"


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
    _unmark_template_deleted(final_name)
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
    if MIGRATION_MARKER.exists():
        return []
    imported = []
    for name, data in (legacy_profiles or {}).items():
        if name in _deleted_templates():
            continue
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
    try:
        MIGRATION_MARKER.write_text("done", encoding="utf-8")
    except Exception:
        pass
    return imported


def delete_template(name: str):
    d = template_dir(name)
    _mark_template_deleted(name)
    if d.exists():
        shutil.rmtree(d)
        return True
    return False


def duplicate_template(name: str):
    src = template_dir(name)
    if not src.exists():
        raise FileNotFoundError(str(src))

    base = f"{name} Copy"
    final = base
    i = 1
    while template_dir(final).exists():
        i += 1
        final = f"{base} {i}"

    dest = template_dir(final)
    shutil.copytree(src, dest)
    data = load_template(final)
    data["name"] = final
    save_template(final, data)
    _unmark_template_deleted(final)
    return data


def rename_template(old_name: str, new_name: str):
    old = template_dir(old_name)
    new = template_dir(new_name)
    if not old.exists():
        raise FileNotFoundError(str(old))
    if new.exists():
        raise FileExistsError(str(new))
    old.rename(new)
    data = load_template(new_name)
    data["name"] = new_name
    save_template(new_name, data)
    _unmark_template_deleted(new_name)
    return data


def default_marker_path():
    ensure_template_root()
    return TEMPLATE_LIBRARY_DIR / ".default_template"


def set_default_template(name: str):
    ensure_template_root()
    default_marker_path().write_text(name, encoding="utf-8")


def get_default_template():
    p = default_marker_path()
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8").strip()


def _deleted_templates():
    ensure_template_root()
    if not DELETED_TEMPLATES_PATH.exists():
        return set()
    return {line.strip() for line in DELETED_TEMPLATES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()}


def _mark_template_deleted(name: str):
    deleted = _deleted_templates()
    deleted.add(name)
    DELETED_TEMPLATES_PATH.write_text("\n".join(sorted(deleted)), encoding="utf-8")


def _unmark_template_deleted(name: str):
    deleted = _deleted_templates()
    if name in deleted:
        deleted.remove(name)
        DELETED_TEMPLATES_PATH.write_text("\n".join(sorted(deleted)), encoding="utf-8")


def ensure_background_file(name: str, data: dict):
    """
    Ensures the template folder contains the background file referenced by template.json.

    Returns:
        (ok: bool, message: str)
    """
    d = template_dir(name)
    d.mkdir(parents=True, exist_ok=True)

    bg = data.get("background", "background.png")
    bg_path = Path(bg)

    # Case 1: background is absolute source path.
    if bg_path.is_absolute() and bg_path.exists():
        suffix = bg_path.suffix.lower() or ".png"
        dest = d / f"background{suffix}"
        try:
            shutil.copy2(bg_path, dest)
            data["background"] = dest.name
            save_template(name, data)
            return dest.exists(), f"{dest.name} kopiert"
        except Exception as e:
            return False, str(e)

    # Case 2: background is relative to template folder and exists.
    resolved = d / bg
    if resolved.exists():
        return True, f"{resolved.name} vorhanden"

    # Case 3: background is relative/absolute but source exists elsewhere.
    if bg and Path(bg).exists():
        src = Path(bg)
        suffix = src.suffix.lower() or ".png"
        dest = d / f"background{suffix}"
        try:
            shutil.copy2(src, dest)
            data["background"] = dest.name
            save_template(name, data)
            return dest.exists(), f"{dest.name} kopiert"
        except Exception as e:
            return False, str(e)

    return False, f"Hintergrunddatei fehlt: {resolved}"
