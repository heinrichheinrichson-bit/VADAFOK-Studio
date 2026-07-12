from __future__ import annotations
import json
from pathlib import Path
from typing import List

def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def favorites_path() -> Path:
    return project_root() / "scene_favorites.json"

def load_favorites() -> List[str]:
    path = favorites_path()
    if not path.exists():
        save_favorites([])
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    seen = set()
    result = []
    for item in data:
        name = str(item).strip()
        if name and name not in seen:
            seen.add(name)
            result.append(name)
    return result

def save_favorites(items: List[str]) -> Path:
    seen = set()
    cleaned = []
    for item in items:
        name = str(item).strip()
        if name and name not in seen:
            seen.add(name)
            cleaned.append(name)
    path = favorites_path()
    path.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def add_favorite(scene_name: str) -> List[str]:
    items = load_favorites()
    scene_name = str(scene_name or "").strip()
    if scene_name and scene_name not in items:
        items.append(scene_name)
        save_favorites(items)
    return items

def remove_favorite(scene_name: str) -> List[str]:
    items = [x for x in load_favorites() if x != scene_name]
    save_favorites(items)
    return items
