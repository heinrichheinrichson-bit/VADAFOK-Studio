from pathlib import Path
from PIL import Image
import io
import base64


def load_rgba(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return Image.open(p).convert("RGBA")


def fit_image_to_box(image, box_width, box_height, padding=30):
    iw, ih = image.size
    box_width = max(100, int(box_width))
    box_height = max(100, int(box_height))
    scale = min((box_width - padding) / iw, (box_height - padding) / ih)
    scale = max(0.01, scale)
    display_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    display = image.resize(display_size)
    offset = ((box_width - display_size[0]) // 2, (box_height - display_size[1]) // 2)
    return display, scale, offset


def pil_to_tk_photo_data(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue())


def image_status(path):
    if not path:
        return {
            "path": "",
            "exists": False,
            "name": "kein Hintergrund",
            "size": "",
            "error": "",
        }
    p = Path(path)
    result = {
        "path": str(p),
        "exists": p.exists(),
        "name": p.name,
        "size": "",
        "error": "",
    }
    if not p.exists():
        result["error"] = "Datei nicht gefunden"
        return result
    try:
        img = Image.open(p)
        result["size"] = f"{img.size[0]} × {img.size[1]}"
    except Exception as e:
        result["error"] = str(e)
    return result
