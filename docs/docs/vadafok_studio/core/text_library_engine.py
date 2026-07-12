from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


DEFAULT_LIBRARY: Dict[str, List[str]] = {
    "Chat": [
        "CHAT WAS RIGHT.",
        "THANKS FOR THE HINT.",
        "GOOD IDEA.",
        "I SEE WHAT YOU MEAN.",
    ],
    "Gameplay": [
        "THAT WAS CLOSE...",
        "I HAVE A BAD FEELING ABOUT THIS.",
        "MAYBE THIS WAS A MISTAKE.",
        "OF COURSE IT WAS A TRAP.",
    ],
    "Humor": [
        "EXACTLY AS PLANNED.",
        "NOBODY SAW THAT.",
        "LET US NEVER SPEAK OF THIS AGAIN.",
        "PROFESSIONAL GAMEPLAY.",
    ],
    "Danger": [
        "SOMETHING IS WRONG HERE.",
        "THIS PLACE FEELS UNSAFE.",
        "I SHOULD BE CAREFUL NOW.",
        "THIS LOOKS LIKE TROUBLE.",
    ],
    "Boss": [
        "NOW THE REAL FIGHT BEGINS.",
        "A WORTHY OPPONENT.",
        "THIS COULD TAKE A WHILE.",
        "EVERY MISTAKE COUNTS NOW.",
    ],
    "Break": [
        "SHORT BREAK.",
        "BE RIGHT BACK.",
        "ONE MOMENT PLEASE.",
    ],
    "Intertitle": [
        "AND SO THE TROUBLE BEGAN.",
        "A NEW CHAPTER BEGINS.",
        "LATER, IN A MUCH WORSE PLACE...",
        "THE JOURNEY CONTINUES.",
    ],
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def library_path() -> Path:
    return project_root() / "text_library.json"


def load_library() -> Dict[str, List[str]]:
    path = library_path()
    if not path.exists():
        save_library(DEFAULT_LIBRARY)
        return dict(DEFAULT_LIBRARY)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        save_library(DEFAULT_LIBRARY)
        return dict(DEFAULT_LIBRARY)
    cleaned = {}
    for category, items in data.items():
        if isinstance(items, list):
            cleaned[str(category)] = [str(x) for x in items]
    return cleaned or dict(DEFAULT_LIBRARY)


def save_library(data: Dict[str, List[str]]) -> Path:
    path = library_path()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def add_category(category: str) -> Dict[str, List[str]]:
    data = load_library()
    category = (category or "").strip()
    if category:
        data.setdefault(category, [])
        save_library(data)
    return data


def rename_category(old_category: str, new_category: str) -> Dict[str, List[str]]:
    data = load_library()
    old_category = (old_category or "").strip()
    new_category = (new_category or "").strip()
    if old_category and new_category and old_category in data and old_category != new_category:
        if new_category in data:
            for item in data.get(old_category, []):
                if item not in data[new_category]:
                    data[new_category].append(item)
            del data[old_category]
        else:
            data[new_category] = data.pop(old_category)
        save_library(data)
    return data


def delete_category(category: str) -> Dict[str, List[str]]:
    data = load_library()
    category = (category or "").strip()
    if category in data:
        del data[category]
        if not data:
            data = dict(DEFAULT_LIBRARY)
        save_library(data)
    return data


def add_text(category: str, text: str) -> Dict[str, List[str]]:
    data = load_library()
    category = (category or "Chat").strip() or "Chat"
    text = (text or "").strip()
    if text:
        data.setdefault(category, [])
        if text not in data[category]:
            data[category].append(text)
        save_library(data)
    return data


def edit_text(category: str, old_text: str, new_text: str) -> Dict[str, List[str]]:
    data = load_library()
    category = (category or "").strip()
    old_text = str(old_text or "")
    new_text = str(new_text or "").strip()
    if category in data and old_text in data[category] and new_text:
        idx = data[category].index(old_text)
        data[category][idx] = new_text
        # remove duplicates while preserving order
        seen = set()
        data[category] = [x for x in data[category] if not (x in seen or seen.add(x))]
        save_library(data)
    return data


def delete_text(category: str, text: str) -> Dict[str, List[str]]:
    data = load_library()
    if category in data and text in data[category]:
        data[category].remove(text)
        save_library(data)
    return data
