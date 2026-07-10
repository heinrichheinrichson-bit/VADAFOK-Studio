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
        "actions": [],
    },
    {
        "name": "Pause",
        "scene": "",
        "banner_text": "One moment, please...",
        "show_banner": True,
        "show_sources": [],
        "hide_sources": [],
        "actions": [],
    },
    {
        "name": "Boss Fight",
        "scene": "",
        "banner_text": "This could get ugly...",
        "show_banner": True,
        "show_sources": [],
        "hide_sources": [],
        "actions": [],
    },
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def presets_path() -> Path:
    return project_root() / "silent_director_presets.json"


def normalize_action(action: Dict[str, Any]) -> Dict[str, Any]:
    action_type = str(action.get("type", "")).strip() or "note"
    return {
        "type": action_type,
        "scene": str(action.get("scene", "")).strip(),
        "text": str(action.get("text", "")).strip(),
        "source": str(action.get("source", "")).strip(),
        "seconds": str(action.get("seconds", "")).strip(),
    }


def legacy_actions_from_preset(preset: Dict[str, Any]) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []

    scene = str(preset.get("scene", "")).strip()
    if scene:
        actions.append({"type": "switch_scene", "scene": scene, "text": "", "source": ""})

    banner_text = str(preset.get("banner_text", "")).strip()
    if bool(preset.get("show_banner", False)) and banner_text:
        actions.append({"type": "show_banner", "scene": "", "text": banner_text, "source": ""})

    for source in preset.get("show_sources", []) or []:
        source = str(source).strip()
        if source:
            actions.append({"type": "show_source", "scene": "", "text": "", "source": source})

    for source in preset.get("hide_sources", []) or []:
        source = str(source).strip()
        if source:
            actions.append({"type": "hide_source", "scene": "", "text": "", "source": source})

    return actions


def normalize_preset(preset: Dict[str, Any]) -> Dict[str, Any]:
    actions = preset.get("actions", None)
    if not isinstance(actions, list):
        actions = legacy_actions_from_preset(preset)

    cleaned_actions = [normalize_action(action) for action in actions if isinstance(action, dict)]

    # Keep legacy fields for compatibility and older UI parts.
    scene = str(preset.get("scene", "")).strip()
    banner_text = str(preset.get("banner_text", "")).strip()
    show_banner = bool(preset.get("show_banner", False))

    if not scene:
        for action in cleaned_actions:
            if action.get("type") == "switch_scene" and action.get("scene"):
                scene = action.get("scene", "")
                break

    if not banner_text:
        for action in cleaned_actions:
            if action.get("type") == "show_banner" and action.get("text"):
                banner_text = action.get("text", "")
                show_banner = True
                break

    return {
        "name": str(preset.get("name", "")).strip() or "Untitled",
        "scene": scene,
        "banner_text": banner_text,
        "show_banner": show_banner,
        "show_sources": [str(x).strip() for x in preset.get("show_sources", []) if str(x).strip()],
        "hide_sources": [str(x).strip() for x in preset.get("hide_sources", []) if str(x).strip()],
        "actions": cleaned_actions,
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
    presets = [normalize_preset(x) for x in data]
    save_presets(presets)
    return presets


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
        "actions": [],
    }))
    save_presets(presets)
    return presets


def delete_preset(name: str) -> List[Dict[str, Any]]:
    presets = [p for p in load_presets() if p.get("name") != name]
    save_presets(presets)
    return presets


def update_preset(old_name: str, updated: Dict[str, Any]) -> List[Dict[str, Any]]:
    presets = load_presets()
    old_name = str(old_name or "").strip()
    normalized = normalize_preset(updated)
    replaced = False
    for idx, preset in enumerate(presets):
        if preset.get("name") == old_name:
            presets[idx] = normalized
            replaced = True
            break
    if not replaced:
        presets.append(normalized)
    save_presets(presets)
    return presets


def add_action(preset_name: str, action: Dict[str, Any]) -> List[Dict[str, Any]]:
    presets = load_presets()
    for preset in presets:
        if preset.get("name") == preset_name:
            preset.setdefault("actions", []).append(normalize_action(action))
            break
    save_presets(presets)
    return presets


def delete_action(preset_name: str, index: int) -> List[Dict[str, Any]]:
    presets = load_presets()
    for preset in presets:
        if preset.get("name") == preset_name:
            actions = preset.setdefault("actions", [])
            if 0 <= index < len(actions):
                del actions[index]
            break
    save_presets(presets)
    return presets


def update_action(preset_name: str, index: int, action: Dict[str, Any]) -> List[Dict[str, Any]]:
    presets = load_presets()
    for preset in presets:
        if preset.get("name") == preset_name:
            actions = preset.setdefault("actions", [])
            if 0 <= index < len(actions):
                actions[index] = normalize_action(action)
            break
    save_presets(presets)
    return presets


def move_action(preset_name: str, index: int, direction: int) -> List[Dict[str, Any]]:
    presets = load_presets()
    for preset in presets:
        if preset.get("name") == preset_name:
            actions = preset.setdefault("actions", [])
            new_index = index + direction
            if 0 <= index < len(actions) and 0 <= new_index < len(actions):
                actions[index], actions[new_index] = actions[new_index], actions[index]
            break
    save_presets(presets)
    return presets
