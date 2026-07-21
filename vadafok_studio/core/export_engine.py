from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple
import tempfile


EXPORT_PROFILES: Dict[str, Dict[str, object]] = {
    "Broadcast PNG": {
        "format": "PNG",
        "suffix": "broadcast",
        "size": None,
        "quality": None,
        "transparent": False,
    },
    "OBS Overlay PNG": {
        "format": "PNG",
        "suffix": "obs_overlay",
        "size": None,
        "quality": None,
        "transparent": True,
    },
    "YouTube Thumbnail JPG": {
        "format": "JPEG",
        "suffix": "youtube_thumb",
        "size": (1280, 720),
        "quality": 95,
        "transparent": False,
    },
    "Instagram Square PNG": {
        "format": "PNG",
        "suffix": "instagram_square",
        "size": (1080, 1080),
        "quality": None,
        "transparent": False,
    },
    "TikTok Vertical PNG": {
        "format": "PNG",
        "suffix": "tiktok_vertical",
        "size": (1080, 1920),
        "quality": None,
        "transparent": False,
    },
}


def list_export_profiles() -> List[str]:
    return list(EXPORT_PROFILES.keys())


def get_export_profile(name: str) -> Dict[str, object]:
    return dict(EXPORT_PROFILES.get(name) or EXPORT_PROFILES["Broadcast PNG"])


def safe_filename(value: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
    return safe or "card"


def export_path(export_dir: Path, base_name: str, profile_name: str, final: bool = True) -> Path:
    profile = get_export_profile(profile_name)
    suffix = profile.get("suffix") or safe_filename(profile_name).lower()
    state = "final" if final else "preview"
    ext = ".jpg" if profile.get("format") == "JPEG" else ".png"
    return export_dir / f"{safe_filename(base_name)}_{suffix}_{state}{ext}"


def apply_export_profile(image, profile_name: str):
    profile = get_export_profile(profile_name)
    target_size = profile.get("size")
    fmt = profile.get("format", "PNG")

    if target_size:
        # Resize to fit into target canvas without distortion, centered.
        from PIL import Image
        base = image.convert("RGBA")
        canvas = Image.new("RGBA", target_size, (0, 0, 0, 0) if profile.get("transparent") else (0, 0, 0, 255))
        fit = base.copy()
        fit.thumbnail(target_size, Image.LANCZOS)
        x = (target_size[0] - fit.size[0]) // 2
        y = (target_size[1] - fit.size[1]) // 2
        canvas.alpha_composite(fit, (x, y))
        image = canvas

    if fmt == "JPEG":
        # JPEG cannot store alpha.
        bg = image.convert("RGBA")
        from PIL import Image
        canvas = Image.new("RGB", bg.size, (0, 0, 0))
        canvas.paste(bg, mask=bg.split()[-1])
        return canvas

    return image.convert("RGBA")


def save_with_profile(image, path: Path, profile_name: str) -> Path:
    profile = get_export_profile(profile_name)
    output = apply_export_profile(image, profile_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        prefix=f".{path.stem}.",
        suffix=f".tmp{path.suffix}",
        dir=path.parent,
        delete=False,
    )
    temporary = Path(handle.name)
    handle.close()
    try:
        if profile.get("format") == "JPEG":
            output.save(
                temporary, "JPEG",
                quality=int(profile.get("quality") or 95), optimize=True,
            )
        else:
            output.save(temporary, "PNG")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return path
