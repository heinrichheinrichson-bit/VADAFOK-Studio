
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
SOUND_EXTS = {".wav", ".mp3", ".ogg", ".flac"}
ROOT_FOLDERS = ["Library", "Live Cards", "Scene Cards", "Banners", "Templates", "Fonts", "Sounds", "Projects"]

@dataclass
class LibraryItem:
    path: Path
    name: str
    section: str
    category: str
    relative: str
    kind: str

def file_kind(path: Path):
    if path.suffix.lower() in IMAGE_EXTS:
        return "image"
    if path.suffix.lower() in SOUND_EXTS:
        return "sound"
    return "file"

def scan_library_section(project_folder: str, section: str):
    """Scan only one selected top-level Library section."""
    base = Path(project_folder) if project_folder else None
    section = str(section or "").strip()

    if not base or not base.exists() or section not in ROOT_FOLDERS:
        return []

    items = []
    root = base / section

    if root.exists():
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in IMAGE_EXTS and path.suffix.lower() not in SOUND_EXTS:
                continue

            relative_parts = path.relative_to(root).parts
            category = relative_parts[0] if len(relative_parts) > 1 else "(Root)"
            items.append(
                LibraryItem(
                    path=path,
                    name=path.name,
                    section=section,
                    category=category,
                    relative=str(path.relative_to(base)),
                    kind=file_kind(path),
                )
            )

    # Preserve the old behavior for loose files in the project root.
    if section in {"Scene Cards", "Sounds"}:
        for path in base.glob("*"):
            if not path.is_file():
                continue

            suffix = path.suffix.lower()
            is_matching = (
                section == "Scene Cards" and suffix in IMAGE_EXTS
            ) or (
                section == "Sounds" and suffix in SOUND_EXTS
            )
            if not is_matching:
                continue

            items.append(
                LibraryItem(
                    path=path,
                    name=path.name,
                    section=section,
                    category="(Root)",
                    relative=str(path.relative_to(base)),
                    kind=file_kind(path),
                )
            )

    return sorted(
        items,
        key=lambda item: (
            item.category.lower(),
            item.name.lower(),
        ),
    )


def library_section_exists(project_folder: str, section: str):
    """Cheap folder availability check without loading images."""
    base = Path(project_folder) if project_folder else None
    if not base or not base.exists():
        return False

    if (base / section).exists():
        return True

    if section == "Scene Cards":
        return any(
            path.is_file() and path.suffix.lower() in IMAGE_EXTS
            for path in base.glob("*")
        )

    if section == "Sounds":
        return any(
            path.is_file() and path.suffix.lower() in SOUND_EXTS
            for path in base.glob("*")
        )

    return False


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
                    path=p, name=p.name, section=root_name, category=category,
                    relative=str(p.relative_to(base)), kind=file_kind(p)
                ))

    for p in base.glob("*"):
        if p.is_file() and (p.suffix.lower() in IMAGE_EXTS or p.suffix.lower() in SOUND_EXTS):
            items.append(LibraryItem(
                path=p, name=p.name,
                section="Scene Cards" if p.suffix.lower() in IMAGE_EXTS else "Sounds",
                category="(Root)", relative=str(p.relative_to(base)), kind=file_kind(p)
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
        "banner": ["banner", "ribbon", "scroll", "band", "banners"],
    }
    for tag, keys in candidates.items():
        if any(k in words for k in keys):
            tags.append(tag)
    return tags
