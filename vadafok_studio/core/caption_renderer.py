"""Smart caption renderer with lightweight caching and detailed profiling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


_FONT_PATH_CACHE: dict[str, Path | None] = {}
_FONT_CACHE: dict[tuple[str, int], ImageFont.ImageFont] = {}
_BANNER_CACHE: dict[str, tuple[int, int, Image.Image]] = {}


def _mark(profiler: Any, name: str) -> None:
    if profiler is not None:
        try:
            profiler.mark(name)
        except Exception:
            pass


def find_font(font_family: str):
    key = str(font_family or "").strip().casefold()
    if key in _FONT_PATH_CACHE:
        return _FONT_PATH_CACHE[key]

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
    result = next((candidate for candidate in candidates if candidate.exists()), None)
    _FONT_PATH_CACHE[key] = result
    return result


def load_font(font_family: str, size: int):
    size = max(1, int(size))
    path = find_font(font_family)
    cache_key = (str(path) if path else "__default__", size)
    cached = _FONT_CACHE.get(cache_key)
    if cached is not None:
        return cached

    font = ImageFont.truetype(str(path), size=size) if path else ImageFont.load_default()
    _FONT_CACHE[cache_key] = font
    return font


def _load_banner(path: str | Path) -> tuple[Image.Image, bool]:
    banner_path = Path(path).resolve()
    stat = banner_path.stat()
    key = str(banner_path)
    cached = _BANNER_CACHE.get(key)
    signature = (stat.st_mtime_ns, stat.st_size)
    if cached is not None and cached[:2] == signature:
        return cached[2], True

    with Image.open(banner_path) as source:
        image = source.convert("RGBA")
        image.load()
    _BANNER_CACHE[key] = (signature[0], signature[1], image)
    return image, False


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
    attempts = 0
    while size >= 12:
        attempts += 1
        font = load_font(font_family, size)
        lines = wrap_text(draw, text, font, max_width, stroke_width)
        boxes = [
            draw.textbbox((0, 0), line or " ", font=font, stroke_width=stroke_width)
            for line in lines
        ]
        heights = [box[3] - box[1] for box in boxes]
        spacing = int(size * 0.18)
        total_h = sum(heights) + max(0, len(lines) - 1) * spacing
        widest = max((box[2] - box[0] for box in boxes), default=0)
        if widest <= max_width and total_h <= max_height:
            return font, lines, size, total_h, attempts
        size -= 4
    font = load_font(font_family, 12)
    return font, wrap_text(draw, text, font, max_width, stroke_width), 12, 12, attempts + 1


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
    safe_left=12,
    safe_right=12,
    safe_top=24,
    safe_bottom=24,
    text_area=None,
    profiler=None,
    png_compress_level=1,
):
    """Create one final transparent PNG and optionally profile each stage."""
    _mark(profiler, "Renderer entered")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    text = (text or "...").strip()
    if uppercase:
        text = text.upper()
    _mark(profiler, f"Render metadata: text_chars={len(text)}")

    banner = None
    if banner_path:
        bp = Path(banner_path)
        if bp.exists():
            _mark(profiler, "Banner load requested")
            banner, cache_hit = _load_banner(bp)
            _mark(profiler, f"Banner load finished: cache={'hit' if cache_hit else 'miss'}")

    if banner is not None:
        img = banner.copy()
        width, height = img.size
        _mark(profiler, "Banner copy finished")
    else:
        img = Image.new("RGBA", (int(width), int(height)), (0, 0, 0, 0))
        width, height = img.size
        _mark(profiler, "Transparent canvas created")

    _mark(profiler, f"Render metadata: image={width}x{height}")
    draw = ImageDraw.Draw(img)
    _mark(profiler, "ImageDraw created")

    if text_area and int(text_area.get("width", 0)) > 0 and int(text_area.get("height", 0)) > 0:
        safe_x = int(text_area.get("x", 0))
        safe_y = int(text_area.get("y", 0))
        safe_w = int(text_area.get("width", width))
        safe_h = int(text_area.get("height", height))
    else:
        safe_left = max(0, min(45, int(safe_left)))
        safe_right = max(0, min(45, int(safe_right)))
        safe_top = max(0, min(45, int(safe_top)))
        safe_bottom = max(0, min(45, int(safe_bottom)))
        pad_left = int(width * (safe_left / 100))
        pad_right = int(width * (safe_right / 100))
        pad_top = int(height * (safe_top / 100))
        pad_bottom = int(height * (safe_bottom / 100))
        safe_x = pad_left
        safe_y = pad_top
        safe_w = max(20, width - pad_left - pad_right)
        safe_h = max(20, height - pad_top - pad_bottom)

    safe_x = max(0, min(width - 20, safe_x))
    safe_y = max(0, min(height - 20, safe_y))
    safe_w = max(20, min(width - safe_x, safe_w))
    safe_h = max(20, min(height - safe_y, safe_h))
    _mark(profiler, f"Text area calculated: {safe_w}x{safe_h}")

    stroke_width = int(stroke_width)
    _mark(profiler, "Font fit requested")
    font, lines, actual_size, total_h, attempts = fit_font(
        draw=draw,
        text=text,
        font_family=font_family,
        max_width=safe_w,
        max_height=safe_h,
        start_size=int(font_size),
        stroke_width=stroke_width,
    )
    _mark(
        profiler,
        f"Font fit finished: size={actual_size} lines={len(lines)} attempts={attempts}",
    )

    spacing = int(actual_size * 0.18)
    y = safe_y + (safe_h - total_h) // 2
    fill = normalize_color(text_color, "#FFFFFF")
    stroke = normalize_color(stroke_color, "#000000")

    _mark(profiler, "Text draw requested")
    for line in lines:
        bbox = draw.textbbox((0, 0), line or " ", font=font, stroke_width=stroke_width)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = safe_x + (safe_w - line_w) // 2
        draw.text(
            (x - bbox[0], y - bbox[1]),
            line,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke,
        )
        y += line_h + spacing
    _mark(profiler, "Text draw finished")

    try:
        png_compress_level = int(png_compress_level)
    except (TypeError, ValueError):
        png_compress_level = 1
    png_compress_level = max(0, min(9, png_compress_level))

    _mark(
        profiler,
        f"PNG save requested: compress_level={png_compress_level}",
    )
    img.save(
        output_path,
        format="PNG",
        compress_level=png_compress_level,
        optimize=False,
    )
    try:
        png_size = output_path.stat().st_size
        _mark(
            profiler,
            (
                f"PNG save finished: bytes={png_size} "
                f"compress_level={png_compress_level}"
            ),
        )
    except OSError:
        _mark(profiler, "PNG save finished")
    return output_path
