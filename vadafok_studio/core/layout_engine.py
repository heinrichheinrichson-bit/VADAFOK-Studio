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


from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def _card_find_font(font_family: str):
    fonts_dir = Path("C:/Windows/Fonts")
    compact = (font_family or "").replace(" ", "")
    for p in [
        fonts_dir / f"{font_family}.ttf",
        fonts_dir / f"{font_family}.otf",
        fonts_dir / f"{compact}.ttf",
        fonts_dir / f"{compact}.otf",
        fonts_dir / "arialbd.ttf",
        fonts_dir / "arial.ttf",
    ]:
        if p.exists():
            return p
    return None

def _card_font(font_family, size):
    p = _card_find_font(font_family)
    if p:
        return ImageFont.truetype(str(p), max(8, int(size)))
    return ImageFont.load_default()

def _card_wrap(draw, text, font, max_width, stroke_width):
    lines = []
    for raw in (text or "").splitlines() or [""]:
        words = raw.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            test = line + " " + word
            box = draw.textbbox((0, 0), test, font=font, stroke_width=stroke_width)
            if box[2] - box[0] <= max_width:
                line = test
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines

def _card_fit(draw, text, field):
    max_w = max(20, int(field.get("width", 100)))
    max_h = max(20, int(field.get("height", 50)))
    size = int(field.get("font_size", 90))
    stroke_width = int(field.get("stroke_width", 3))
    family = field.get("font_family", "Bebas Neue")
    while size >= 8:
        font = _card_font(family, size)
        lines = _card_wrap(draw, text, font, max_w, stroke_width)
        boxes = [draw.textbbox((0, 0), line or " ", font=font, stroke_width=stroke_width) for line in lines]
        spacing = int(size * 0.14)
        total_h = sum(b[3] - b[1] for b in boxes) + max(0, len(lines)-1) * spacing
        widest = max((b[2]-b[0] for b in boxes), default=0)
        if widest <= max_w and total_h <= max_h:
            return font, lines, total_h, spacing
        size -= 3
    font = _card_font(family, 8)
    return font, _card_wrap(draw, text, font, max_w, stroke_width), 8, 1

def render_template_card_image(template, values, background_path=None, size=None, background_image=None):
    """Render a template to a PIL image without writing a temporary file."""
    bg = None
    if background_image is not None:
        bg = background_image.convert("RGBA")
    elif background_path:
        p = Path(background_path)
        if p.exists():
            with Image.open(p) as source:
                bg = source.convert("RGBA")

    if bg is not None:
        img = bg.copy()
        if size is not None:
            img = img.resize(size)
    else:
        if size is None:
            size = (1280, 720)
        img = Image.new("RGBA", size, (10, 10, 10, 255))

    draw = ImageDraw.Draw(img)

    for field in template.get("fields", []):
        if field.get("hidden", False):
            continue
        name = field.get("name", "field")
        text = values.get(name, "")
        if field.get("uppercase", True):
            text = text.upper()

        stroke_width = int(field.get("stroke_width", 3))
        font, lines, total_h, spacing = _card_fit(draw, text, field)

        x = int(field.get("x", 0))
        y = int(field.get("y", 0))
        w = int(field.get("width", 100))
        h = int(field.get("height", 50))
        cy = y + (h - total_h) // 2

        for line in lines:
            box = draw.textbbox((0, 0), line or " ", font=font, stroke_width=stroke_width)
            line_w = box[2] - box[0]
            line_h = box[3] - box[1]
            tx = x + (w - line_w) // 2
            draw.text(
                (tx - box[0], cy - box[1]),
                line,
                font=font,
                fill=field.get("text_color", "#FFFFFF"),
                stroke_width=stroke_width,
                stroke_fill=field.get("stroke_color", "#000000"),
            )
            cy += line_h + spacing

    return img


def render_template_card(template, values, output_path, background_path=None, size=None):
    """Render a template and save it to *output_path*."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = render_template_card_image(
        template,
        values,
        background_path=background_path,
        size=size,
    )
    img.save(output_path)
    return output_path
