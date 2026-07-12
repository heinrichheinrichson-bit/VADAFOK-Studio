from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


DEFAULT_LIBRARY: Dict[str, List[str]] = {
    "Gameplay": [
        "Das war knapp...",
        "Ich habe da ein ganz schlechtes Gefühl.",
        "Vielleicht war das keine gute Idee.",
        "Natürlich war das eine Falle.",
    ],
    "Humor": [
        "Das war exakt so geplant.",
        "Niemand hat etwas gesehen.",
        "Wir ignorieren diesen Moment einfach.",
        "Professionelles Gameplay.",
    ],
    "Gefahr": [
        "Etwas stimmt hier nicht.",
        "Die Stimmung wird unangenehm.",
        "Ich sollte jetzt besser vorsichtig sein.",
        "Das sieht nach Ärger aus.",
    ],
    "Boss": [
        "Der eigentliche Kampf beginnt jetzt.",
        "Ein würdiger Gegner.",
        "Das könnte länger dauern.",
        "Jetzt zählt jeder Fehler.",
    ],
    "Pause": [
        "Kurze Pause.",
        "Bin gleich zurück.",
        "Einen Moment bitte.",
    ],
    "Chat": [
        "Danke für den Hinweis!",
        "Gute Idee.",
        "Das probiere ich gleich aus.",
        "Ich sehe, was du meinst.",
    ],
    "Intertitle": [
        "Kapitel beginnt.",
        "Und so nahm das Unheil seinen Lauf.",
        "Ein neuer Abschnitt der Reise.",
        "Später, an einem deutlich schlechteren Ort...",
    ],
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def library_path() -> Path:
    return project_root() / "caption_library.json"


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

    cleaned: Dict[str, List[str]] = {}
    for category, items in data.items():
        if isinstance(items, list):
            cleaned[str(category)] = [str(x) for x in items]
    return cleaned or dict(DEFAULT_LIBRARY)


def save_library(data: Dict[str, List[str]]) -> Path:
    path = library_path()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def add_caption(category: str, text: str) -> Dict[str, List[str]]:
    data = load_library()
    category = (category or "Gameplay").strip() or "Gameplay"
    text = (text or "").strip()
    if not text:
        return data
    data.setdefault(category, [])
    if text not in data[category]:
        data[category].append(text)
    save_library(data)
    return data


def delete_caption(category: str, text: str) -> Dict[str, List[str]]:
    data = load_library()
    if category in data and text in data[category]:
        data[category].remove(text)
    save_library(data)
    return data
