
import json
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = APP_ROOT / "data"
EXPORT_DIR = APP_ROOT / "exports"
CONFIG_PATH = DATA_DIR / "config.json"
FAVORITES_PATH = DATA_DIR / "favorites.json"
ASSET_META_PATH = DATA_DIR / "asset_meta.json"
BANNER_PROFILES_PATH = DATA_DIR / "banner_profiles.json"
TEMPLATE_PROFILES_PATH = DATA_DIR / "template_profiles.json"
TEMPLATE_LIBRARY_DIR = DATA_DIR / "templates"
CARD_VALUES_PATH = DATA_DIR / "card_values.json"

DEFAULT_CONFIG = {
    "project_folder": "",
    "host": "localhost",
    "port": "4455",
    "password": "",
    "scene_name": "",
    "caption_group": "VADAFOK Caption",
    "caption_text": "VADAFOK Caption Text",
    "caption_banner_source": "VADAFOK Caption Banner",
    "caption_render_source": "VADAFOK Caption Render",
    "scene_card_source": "VADAFOK Scene Card",
    "duration": "5",
    "style": "Gold Ribbon",
    "selected_banner_path": "",
    "selected_sound_effect": "",
    "stream_effect_enabled": False,
    "stream_effect_source": "VADAFOK Stream Effect",
    "sync_profiler_enabled": True,
    "caption_engine": "obs_text",
    "caption_font_family": "Bebas Neue",
    "caption_font_size": 160,
    "caption_text_color": "#FFFFFF",
    "caption_stroke_color": "#000000",
    "caption_stroke_width": 3,
    "caption_render_width": 1600,
    "caption_render_height": 260,
    "caption_uppercase": True,

    "caption_safe_left": 12,
    "caption_safe_right": 12,
    "caption_safe_top": 24,
    "caption_safe_bottom": 24,
    "voice_enabled": False,
    "voice_trigger_phrase": "live card",
    "voice_culture": "de-DE",
    "banner_sources": {
        "Gold Ribbon": "VADAFOK Banner",
        "Black Gold Plate": "VADAFOK Banner Plate",
        "Paper Scroll": "VADAFOK Banner Scroll",
        "Film Strip": "VADAFOK Banner Filmstrip",
        "Silent Card": "VADAFOK Banner Silent"
    }
}

DEFAULT_FAVORITES = {
    "Reaction": ["OOPS.", "THAT WAS CLOSE.", "SUCCESS!", "ONE MORE TRY..."],
    "Chat Help": ["CHAT WAS RIGHT.", "I NEED YOUR HELP...", "ANY IDEAS?", "WHAT WOULD YOU DO?"],
    "Rules": ["PLEASE NO SPOILERS.", "PLEASE NO BACKSEATING.", "HINTS ONLY, PLEASE."],
    "Horror": ["I HAVE A BAD FEELING...", "WHY IS IT SO QUIET...?", "I DON'T LIKE THIS..."]
}

DEFAULT_ASSET_META = {"favorites": [], "tags": {}}

def ensure_data():
    DATA_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)

def save_json(path, data):
    ensure_data()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def load_json(path, default):
    ensure_data()
    if not path.exists():
        save_json(path, default)
        return default.copy() if isinstance(default, dict) else list(default)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(default, dict):
            merged = default.copy()
            merged.update(data)
            if "banner_sources" in default:
                bs = default["banner_sources"].copy()
                bs.update(data.get("banner_sources", {}))
                merged["banner_sources"] = bs
            return merged
        return data
    except Exception:
        return default.copy() if isinstance(default, dict) else list(default)

def load_config():
    return load_json(CONFIG_PATH, DEFAULT_CONFIG)

def save_config(config):
    save_json(CONFIG_PATH, config)

def load_favorites():
    return load_json(FAVORITES_PATH, DEFAULT_FAVORITES)

def save_favorites(favorites):
    save_json(FAVORITES_PATH, favorites)

def load_asset_meta():
    return load_json(ASSET_META_PATH, DEFAULT_ASSET_META)

def save_asset_meta(meta):
    save_json(ASSET_META_PATH, meta)
