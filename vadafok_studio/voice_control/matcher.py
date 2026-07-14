"""Controlled fuzzy matching for VADAFOK voice input.

The matcher never writes to Quick Cards. It reads a separate voice library and,
when available, the existing Quick Card text library as additional read-only
phrase candidates.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

_LIBRARY_PATH = Path(__file__).with_name("voice_library.json")
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_QUICK_CARD_CANDIDATES = (
    _PROJECT_ROOT / "docs" / "text_library.json",
    _PROJECT_ROOT / "text_library.json",
)


@dataclass(frozen=True)
class CommandMatch:
    action: str | None
    wake_detected: bool
    score: float
    recognized: str


@dataclass(frozen=True)
class PhraseMatch:
    text: str
    score: float
    source: str


def normalize_text(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except (OSError, ValueError, TypeError):
        return None


def _voice_library() -> dict[str, Any]:
    data = _load_json(_LIBRARY_PATH)
    return data if isinstance(data, dict) else {}


def _similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def _best_similarity(value: str, candidates: Iterable[str]) -> tuple[float, str]:
    best_score = 0.0
    best_candidate = ""
    for candidate in candidates:
        normalized = normalize_text(candidate)
        score = _similarity(value, normalized)
        if score > best_score:
            best_score = score
            best_candidate = normalized
    return best_score, best_candidate


def classify_command(value: Any) -> CommandMatch:
    """Return a command action and block unknown wake-word phrases.

    A phrase that looks like a VADAFOK wake phrase is never allowed to fall
    through into the visible caption, even when no command action is certain.
    """

    normalized = normalize_text(value)
    library = _voice_library()
    thresholds = library.get("thresholds", {})
    command_threshold = float(thresholds.get("command", 0.82))
    wake_threshold = float(thresholds.get("wake", 0.72))

    wake_aliases = [normalize_text(x) for x in library.get("wake_aliases", [])]
    wake_aliases = [x for x in wake_aliases if x]
    if not wake_aliases:
        wake_aliases = ["vadafok"]

    # Compare the beginning of the result against one- and multi-word aliases.
    wake_detected = False
    wake_score = 0.0
    for alias in wake_aliases:
        words = alias.split()
        prefix = " ".join(normalized.split()[: len(words)])
        score = _similarity(prefix, alias)
        if score > wake_score:
            wake_score = score
        if score >= wake_threshold:
            wake_detected = True

    commands = library.get("commands", {})
    if not isinstance(commands, dict):
        commands = {}

    best_action: str | None = None
    best_score = 0.0
    for action, phrases in commands.items():
        if not isinstance(phrases, list):
            continue
        score, _ = _best_similarity(normalized, (str(x) for x in phrases))
        if score > best_score:
            best_score = score
            best_action = str(action)

    if best_action is not None and best_score >= command_threshold:
        return CommandMatch(best_action, True, best_score, normalized)

    return CommandMatch(None, wake_detected, max(best_score, wake_score), normalized)


def _flatten_quick_cards(data: Any) -> list[str]:
    phrases: list[str] = []
    if isinstance(data, dict):
        for value in data.values():
            phrases.extend(_flatten_quick_cards(value))
    elif isinstance(data, list):
        for value in data:
            if isinstance(value, str) and value.strip():
                phrases.append(value.strip())
            else:
                phrases.extend(_flatten_quick_cards(value))
    return phrases


def _known_phrases() -> list[tuple[str, str]]:
    library = _voice_library()
    seen: set[str] = set()
    result: list[tuple[str, str]] = []

    for phrase in library.get("phrases", []):
        if not isinstance(phrase, str) or not phrase.strip():
            continue
        key = normalize_text(phrase)
        if key and key not in seen:
            seen.add(key)
            result.append((phrase.strip(), "voice library"))

    # Existing Quick Cards are an optional, read-only source. Their file is
    # never modified by the voice matcher.
    for path in _QUICK_CARD_CANDIDATES:
        data = _load_json(path)
        if data is None:
            continue
        for phrase in _flatten_quick_cards(data):
            key = normalize_text(phrase)
            if key and key not in seen:
                seen.add(key)
                result.append((phrase, "quick cards"))
        break

    return result


def match_known_phrase(value: Any) -> PhraseMatch | None:
    """Return a confident prepared-text correction, otherwise ``None``.

    TEST 07 checks explicit aliases first. This is important for recurring
    recognizer mistakes such as ``thank you for 40`` ->
    ``Thank you for the follow.``. Aliases live only in the Voice Library and
    never modify Quick Cards.
    """

    original = str(value or "").strip()
    normalized = normalize_text(original)
    if len(normalized) < 4:
        return None

    library = _voice_library()

    aliases = library.get("aliases", {})
    if isinstance(aliases, dict):
        for heard_variant, corrected_text in aliases.items():
            if not isinstance(heard_variant, str) or not isinstance(corrected_text, str):
                continue
            if normalize_text(heard_variant) == normalized and corrected_text.strip():
                return PhraseMatch(corrected_text.strip(), 1.0, "voice alias")

    thresholds = library.get("thresholds", {})
    long_threshold = float(thresholds.get("phrase", 0.86))
    short_threshold = float(thresholds.get("short_phrase", 0.95))

    best: PhraseMatch | None = None
    for candidate, source in _known_phrases():
        candidate_normalized = normalize_text(candidate)
        if not candidate_normalized:
            continue

        # Avoid replacing an unrelated sentence merely because a short phrase
        # happens to be contained in it.
        length_ratio = min(len(normalized), len(candidate_normalized)) / max(
            len(normalized), len(candidate_normalized)
        )
        if length_ratio < 0.65:
            continue

        score = _similarity(normalized, candidate_normalized)
        threshold = short_threshold if len(candidate_normalized) < 12 else long_threshold
        if score < threshold:
            continue
        if best is None or score > best.score:
            best = PhraseMatch(candidate, score, source)

    return best
