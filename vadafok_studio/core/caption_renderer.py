
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def find_font(font_family: str):
    fonts_dir = Path("C:/Windows/Fonts")
    family = (font_family or "").replace(" ", "")
    candidates = [
        fonts_dir / f"{font_family}.ttf",
        fonts_dir / f"{font_family}.otf",
        fonts_dir / f"{family}.ttf",
        fonts_dir / f"{family}.otf",
        fonts_dir / "arialbd.ttf",
        fonts_dir / "arial.ttf",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

def load_font(font_family: str, size: int):
    path = find_font(font_family)
    if path:
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()

def normalize_color(value, fallback):
    value = (value or "").strip()
    if value.startswith("#") and len(value) in (7, 9):
        return value
    return fallback

def wrap_text(draw, text, font, max_width, stroke_width=0):
    lines = []
    raw_lines = text.splitlines() if text else [""]
    for raw in raw_lines:
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

def fit_font(draw, text, font_family, max_width, max_height, start_size, stroke_width):
    size = int(start_size)
    while size >= 12:
        font = load_font(font_family, size)
        lines = wrap_text(draw, text, font, max_width, stroke_width)
        boxes = [draw.textbbox((0, 0), line or " ", font=font, stroke_width=stroke_width) for line in lines]
        heights = [b[3] - b[1] for b in boxes]
        spacing = int(size * 0.18)
        total_h = sum(heights) + max(0, len(lines) - 1) * spacing
        widest = max((b[2] - b[0] for b in boxes), default=0)
        if widest <= max_width and total_h <= max_height:
            return font, lines, size, total_h
        size -= 4
    font = load_font(font_family, 12)
    return font, wrap_text(draw, text, font, max_width, stroke_width), 12, 12

def render_caption_png(
    text,
    output_path,
    width=1600,
    height=260,
    font_family="Bebas Neue",
    font_size=160,
    text_color="#FFFFFF",
    stroke_color="#000000",
    stroke_width=3,
    uppercase=True,
    banner_path="",
):
    """
    Studio 0.7:
    Creates ONE final transparent PNG:
    selected banner + centered text.

    OBS should only show this final PNG via VADAFOK Caption Render.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    text = (text or "...").strip()
    if uppercase:
        text = text.upper()

    # If a banner exists, render at banner size.
    banner = None
    if banner_path:
        bp = Path(banner_path)
        if bp.exists():
            banner = Image.open(bp).convert("RGBA")

    if banner is not None:
        img = banner.copy()
        width, height = img.size
    else:
        img = Image.new("RGBA", (int(width), int(height)), (0, 0, 0, 0))
        width, height = img.size

    draw = ImageDraw.Draw(img)

    # Text-safe area. For ornate banners, keep away from borders/decorations.
    pad_x = int(width * 0.12)
    pad_y = int(height * 0.22)
    max_w = max(20, width - pad_x * 2)
    max_h = max(20, height - pad_y * 2)

    stroke_width = int(stroke_width)
    font, lines, actual_size, total_h = fit_font(
        draw=draw,
        text=text,
        font_family=font_family,
        max_width=max_w,
        max_height=max_h,
        start_size=int(font_size),
        stroke_width=stroke_width,
    )

    spacing = int(actual_size * 0.18)
    y = (height - total_h) // 2

    fill = normalize_color(text_color, "#FFFFFF")
    stroke = normalize_color(stroke_color, "#000000")

    for line in lines:
        bbox = draw.textbbox((0, 0), line or " ", font=font, stroke_width=stroke_width)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = (width - line_w) // 2

        # bbox offset prevents ascender clipping.
        draw.text(
            (x - bbox[0], y - bbox[1]),
            line,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke,
        )
        y += line_h + spacing

    img.save(output_path)
    return output_path
