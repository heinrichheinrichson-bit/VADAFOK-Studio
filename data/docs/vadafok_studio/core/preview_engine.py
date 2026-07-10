from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple
from PIL import Image
import io
import base64


@dataclass
class PreviewTransform:
    original_size: Tuple[int, int]
    display_size: Tuple[int, int]
    offset: Tuple[int, int]
    scale: float

    def to_screen_rect(self, x: int, y: int, width: int, height: int) -> tuple[int, int, int, int]:
        ox, oy = self.offset
        s = self.scale
        return (
            ox + int(x * s),
            oy + int(y * s),
            ox + int((x + width) * s),
            oy + int((y + height) * s),
        )

    def from_screen_delta(self, dx: int, dy: int) -> tuple[int, int]:
        s = self.scale or 1.0
        return int(dx / s), int(dy / s)


def load_rgba(path: str | Path) -> Image.Image:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return Image.open(p).convert("RGBA")


def fit_to_box(image: Image.Image, canvas_width: int, canvas_height: int, padding: int = 40) -> tuple[Image.Image, PreviewTransform]:
    iw, ih = image.size
    cw = max(100, int(canvas_width))
    ch = max(100, int(canvas_height))
    usable_w = max(10, cw - padding)
    usable_h = max(10, ch - padding)
    scale = min(usable_w / iw, usable_h / ih)
    scale = max(0.01, scale)
    dw = max(1, int(iw * scale))
    dh = max(1, int(ih * scale))
    display = image.resize((dw, dh))
    offset = ((cw - dw) // 2, (ch - dh) // 2)
    return display, PreviewTransform(
        original_size=(iw, ih),
        display_size=(dw, dh),
        offset=offset,
        scale=scale,
    )


def pil_to_tk_data(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue())


def status_for_path(path: str | Path | None) -> dict:
    if not path:
        return {"name": "kein Hintergrund", "exists": False, "size": "", "path": "", "error": ""}
    p = Path(path)
    result = {"name": p.name, "exists": p.exists(), "size": "", "path": str(p), "error": ""}
    if p.exists():
        try:
            with Image.open(p) as img:
                result["size"] = f"{img.size[0]} × {img.size[1]}"
        except Exception as e:
            result["error"] = str(e)
    else:
        result["error"] = "Datei nicht gefunden"
    return result
