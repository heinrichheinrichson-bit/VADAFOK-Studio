from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class LayoutField:
    name: str
    x: int
    y: int
    width: int
    height: int
    font_family: str = "Bebas Neue"
    font_size: int = 160
    text_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: int = 3
    uppercase: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def banner_profile_to_layout_field(profile: Dict[str, Any], name: str = "caption") -> LayoutField:
    area = profile.get("text_area", {}) or {}
    return LayoutField(
        name=name,
        x=int(area.get("x", 0)),
        y=int(area.get("y", 0)),
        width=int(area.get("width", 0)),
        height=int(area.get("height", 0)),
        font_family=profile.get("font_family", "Bebas Neue"),
        font_size=int(profile.get("font_size", 160)),
        text_color=profile.get("text_color", "#FFFFFF"),
        stroke_color=profile.get("stroke_color", "#000000"),
        stroke_width=int(profile.get("stroke_width", 3)),
        uppercase=bool(profile.get("uppercase", True)),
    )


def apply_layout_field_to_banner_profile(profile: Dict[str, Any], field: LayoutField) -> Dict[str, Any]:
    profile["text_area"] = {
        "x": int(field.x),
        "y": int(field.y),
        "width": int(field.width),
        "height": int(field.height),
    }
    profile["font_family"] = field.font_family
    profile["font_size"] = int(field.font_size)
    profile["text_color"] = field.text_color
    profile["stroke_color"] = field.stroke_color
    profile["stroke_width"] = int(field.stroke_width)
    profile["uppercase"] = bool(field.uppercase)
    return profile


def create_default_template(name="New Template"):
    return {
        "name": name,
        "background": "",
        "fields": [
            LayoutField(name="date", x=120, y=80, width=420, height=90, font_size=90).to_dict(),
            LayoutField(name="game", x=120, y=190, width=900, height=120, font_size=110).to_dict(),
            LayoutField(name="time", x=120, y=340, width=360, height=90, font_size=90).to_dict(),
        ]
    }


def load_template_profiles(load_json_func, path):
    return load_json_func(path, {})


def save_template_profiles(save_json_func, path, profiles):
    save_json_func(path, profiles)
