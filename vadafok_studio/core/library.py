
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

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
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                rel_parts = p.relative_to(root).parts
                category = rel_parts[0] if len(rel_parts) > 1 else "(Root)"
                items.append(LibraryItem(
                    path=p,
                    name=p.name,
                    section=root_name,
                    category=category,
                    relative=str(p.relative_to(base))
                ))

    # Also include loose images directly in project folder as Scene Cards / Root.
    for p in base.glob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            items.append(LibraryItem(
                path=p,
                name=p.name,
                section="Scene Cards",
                category="(Root)",
                relative=str(p.relative_to(base))
            ))

    return sorted(items, key=lambda i: (i.section.lower(), i.category.lower(), i.name.lower()))
