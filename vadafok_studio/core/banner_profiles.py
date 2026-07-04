from .config import BANNER_PROFILES_PATH, save_json, load_json

DEFAULT_BANNER_PROFILE = {
    "text_area": {"x": 0, "y": 0, "width": 0, "height": 0},
    "font_family": "Bebas Neue",
    "font_size": 160,
    "uppercase": True,
    "text_color": "#FFFFFF",
    "stroke_color": "#000000",
    "stroke_width": 3,
    "notes": ""
}

def load_banner_profiles():
    return load_json(BANNER_PROFILES_PATH, {})

def save_banner_profiles(profiles):
    save_json(BANNER_PROFILES_PATH, profiles)

def has_profile(profiles, key):
    return key in profiles

def get_profile(profiles, key):
    return profiles.get(key)

def create_default_profile():
    return {
        "text_area": dict(DEFAULT_BANNER_PROFILE["text_area"]),
        "font_family": DEFAULT_BANNER_PROFILE["font_family"],
        "font_size": DEFAULT_BANNER_PROFILE["font_size"],
        "uppercase": DEFAULT_BANNER_PROFILE["uppercase"],
        "text_color": DEFAULT_BANNER_PROFILE["text_color"],
        "stroke_color": DEFAULT_BANNER_PROFILE["stroke_color"],
        "stroke_width": DEFAULT_BANNER_PROFILE["stroke_width"],
        "notes": DEFAULT_BANNER_PROFILE["notes"],
    }

def ensure_profile(profiles, key):
    if key not in profiles:
        profiles[key] = create_default_profile()
    return profiles[key]

def delete_profile(profiles, key):
    if key in profiles:
        del profiles[key]
        return True
    return False

def profile_count(profiles):
    return len(profiles)
