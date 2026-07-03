
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
SOUND_EXTS = {".wav", ".mp3", ".ogg", ".flac"}

ROOT_FOLDERS = [
    "Library",
    "Live Cards",
    "Scene Cards",
    "Banners",
    "Templates",
    "Fonts",
    "Sounds",
    "Projects",
]

@dataclass
class LibraryItem:
    path: Path
    name: str
    section: str
    category: str
    relative: str
    kind: str

def file_kind(path: Path):
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in SOUND_EXTS:
        return "sound"
    return "file"

def scan_library(project_folder: str):
    base = Path(project_folder) if project_folder else None
    if not base or not base.exists():
        return []

    items = []
    for root_name in ROOT_FOLDERS:
        root = base / root_name
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file() and (p.suffix.lower() in IMAGE_EXTS or p.suffix.lower() in SOUND_EXTS):
                rel_parts = p.relative_to(root).parts
                category = rel_parts[0] if len(rel_parts) > 1 else "(Root)"
                items.append(LibraryItem(
                    path=p,
                    name=p.name,
                    section=root_name,
                    category=category,
                    relative=str(p.relative_to(base)),
                    kind=file_kind(p)
                ))

    for p in base.glob("*"):
        if p.is_file() and (p.suffix.lower() in IMAGE_EXTS or p.suffix.lower() in SOUND_EXTS):
            items.append(LibraryItem(
                path=p,
                name=p.name,
                section="Scene Cards" if p.suffix.lower() in IMAGE_EXTS else "Sounds",
                category="(Root)",
                relative=str(p.relative_to(base)),
                kind=file_kind(p)
            ))

    return sorted(items, key=lambda i: (i.section.lower(), i.category.lower(), i.name.lower()))

def guessed_tags(item: LibraryItem):
    words = (item.name + " " + item.category + " " + item.section).lower()
    tags = []
    candidates = {
        "funny": ["funny", "sarcastic", "oops", "lol"],
        "scary": ["afraid", "horror", "scary", "fear"],
        "chat": ["chat", "help", "question"],
        "schedule": ["schedule", "week", "weekly", "tomorrow", "today"],
        "ending": ["end", "ending", "show-ende", "to be continued"],
        "raid": ["raid"],
        "donation": ["donation"],
        "welcome": ["welcome"],
        "success": ["success"],
        "tip": ["tip", "tips"],
    }
    for tag, keys in candidates.items():
        if any(k in words for k in keys):
            tags.append(tag)
    return tags
