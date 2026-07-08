from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Any


DEFAULT_PRESETS = [
    {
        "name": "Gameplay",
        "scene": "",
        "banner_text": "Back to the adventure.",
        "show_banner": False,
        "show_sources": [],
        "hide_sources": [],
    },
    {
        "name": "Pause",
        "scene": "",
        "banner_text": "One moment, please...",
        "show_banner": True,
        "show_sources": [],
        "hide_sources": [],
    },
    {
        "name": "Boss Fight",
        "scene": "",
        "banner_text": "This could get ugly...",
        "show_banner": True,
        "show_sources": [],
        "hide_sources": [],
    },
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def presets_path() -> Path:
    return project_root() / "silent_director_presets.json"


def normalize_preset(preset: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": str(preset.get("name", "")).strip() or "Untitled",
        "scene": str(preset.get("scene", "")).strip(),
        "banner_text": str(preset.get("banner_text", "")).strip(),
        "show_banner": bool(preset.get("show_banner", False)),
        "show_sources": [str(x).strip() for x in preset.get("show_sources", []) if str(x).strip()],
        "hide_sources": [str(x).strip() for x in preset.get("hide_sources", []) if str(x).strip()],
    }


def load_presets() -> List[Dict[str, Any]]:
    path = presets_path()
    if not path.exists():
        save_presets(DEFAULT_PRESETS)
        return [normalize_preset(x) for x in DEFAULT_PRESETS]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = DEFAULT_PRESETS
    if not isinstance(data, list):
        data = DEFAULT_PRESETS
    return [normalize_preset(x) for x in data]


def save_presets(presets: List[Dict[str, Any]]) -> Path:
    cleaned = [normalize_preset(x) for x in presets]
    path = presets_path()
    path.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def add_preset(name: str, scene: str = "", banner_text: str = "", show_banner: bool = False) -> List[Dict[str, Any]]:
    presets = load_presets()
    presets.append(normalize_preset({
        "name": name,
        "scene": scene,
        "banner_text": banner_text,
        "show_banner": show_banner,
        "show_sources": [],
        "hide_sources": [],
    }))
    save_presets(presets)
    return presets


def delete_preset(name: str) -> List[Dict[str, Any]]:
    presets = [p for p in load_presets() if p.get("name") != name]
    save_presets(presets)
    return presets
