"""Safe voice-assisted Quick Card search for VADAFOK Studio.

The Quick Card library is read-only. All Tk/CustomTkinter UI work happens on
Tk's main thread. Suggestions can be selected by mouse or fixed voice commands.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable

from .voice_help import add_voice_help


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_CANDIDATES = (
    _PROJECT_ROOT / "text_library.json",
    _PROJECT_ROOT / "docs" / "text_library.json",
)
_MIN_SUGGESTION_SCORE = 0.60


@dataclass(frozen=True)
class QuickCardMatch:
    text: str
    category: str
    score: float


def _normalize(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _load_cards() -> list[tuple[str, str]]:
    for path in _LIBRARY_CANDIDATES:
        try:
            with path.open("r", encoding="utf-8-sig") as handle:
                data = json.load(handle)
        except (OSError, ValueError, TypeError):
            continue

        if not isinstance(data, dict):
            continue

        cards: list[tuple[str, str]] = []
        seen: set[str] = set()
        for category, values in data.items():
            if not isinstance(values, list):
                continue
            for value in values:
                text = str(value or "").strip()
                key = _normalize(text)
                if not text or not key or key in seen:
                    continue
                seen.add(key)
                cards.append((str(category), text))
        if cards:
            return cards
    return []


def find_quick_card_matches(
    query: str,
    limit: int = 3,
    minimum_score: float = _MIN_SUGGESTION_SCORE,
) -> list[QuickCardMatch]:
    """Return only credible matches, never merely the least-bad cards."""

    normalized_query = _normalize(query)
    if not normalized_query:
        return []

    matches: list[QuickCardMatch] = []
    query_words = set(normalized_query.split())
    for category, text in _load_cards():
        normalized_card = _normalize(text)
        if not normalized_card:
            continue
        sequence_score = SequenceMatcher(None, normalized_query, normalized_card).ratio()
        card_words = set(normalized_card.split())
        overlap = len(query_words & card_words) / max(1, len(query_words | card_words))
        contains_bonus = 0.08 if (
            normalized_query in normalized_card or normalized_card in normalized_query
        ) else 0.0
        score = min(1.0, (sequence_score * 0.78) + (overlap * 0.22) + contains_bonus)
        if score >= minimum_score:
            matches.append(QuickCardMatch(text=text, category=category, score=score))

    matches.sort(key=lambda item: item.score, reverse=True)
    return matches[: max(1, int(limit))]


def replace_quick_caption_text(app: Any, text: str) -> bool:
    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        return False
    try:
        entry.delete("1.0", "end")
        entry.insert("1.0", text)
        entry.mark_set("insert", "end")
        entry.see("end")
        entry.focus_set()
        return True
    except Exception:
        return False


def close_voice_quick_card_window(app: Any) -> None:
    window = getattr(app, "voice_quick_card_window", None)
    app.voice_quick_card_window = None
    app.voice_quick_card_matches = []
    app.voice_quick_card_query = ""
    if window is None:
        return
    try:
        if window.winfo_exists():
            window.destroy()
    except Exception:
        pass


def voice_quick_card_window_is_open(app: Any) -> bool:
    window = getattr(app, "voice_quick_card_window", None)
    try:
        return bool(window is not None and window.winfo_exists())
    except Exception:
        return False


def _position_near_parent(window: Any, parent: Any) -> None:
    try:
        parent.update_idletasks()
        window.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
        ww, wh = max(window.winfo_reqwidth(), 660), max(window.winfo_reqheight(), 440)

        x = px + pw + 16
        y = py
        if x + ww > sw - 20:
            x = px
            y = py + ph + 16
        x = max(20, min(x, sw - ww - 20))
        y = max(20, min(y, sh - wh - 60))
        window.geometry(f"{ww}x{wh}+{x}+{y}")
    except Exception:
        window.geometry("680x440")


def select_voice_quick_card(app: Any, index: int) -> bool:
    matches = list(getattr(app, "voice_quick_card_matches", []) or [])
    if index < 1 or index > len(matches):
        return False
    callback = getattr(app, "voice_quick_card_finish", None)
    if not callable(callback):
        return False
    match = matches[index - 1]
    callback(
        match.text,
        f"QUICK CARD {index} SELECTED · {match.category} · say VADAFOK SHOW",
    )
    return True


def use_recognized_voice_quick_card_text(app: Any) -> bool:
    query = str(getattr(app, "voice_quick_card_query", "") or "").strip()
    callback = getattr(app, "voice_quick_card_finish", None)
    if not query or not callable(callback):
        return False
    callback(query, "FREE DICTATION USED · say VADAFOK SHOW")
    return True


def show_quick_card_matches(
    app: Any,
    query: str,
    on_finished: Callable[[], None] | None = None,
) -> bool:
    """Show credible results, or a clear no-match state, in a safe window."""

    matches = find_quick_card_matches(query, limit=3)
    parent = getattr(app, "quick_window", None)
    try:
        if parent is None or not parent.winfo_exists():
            return False
    except Exception:
        return False

    try:
        import customtkinter as ctk
    except Exception:
        return False

    close_voice_quick_card_window(app)
    app.voice_quick_card_matches = matches
    app.voice_quick_card_query = query.strip()
    window = None

    def finish_with_text(text: str, status: str) -> None:
        replace_quick_caption_text(app, text)
        app.voice_quick_card_mode = False
        try:
            app.voice_status_var.set(status)
        except Exception:
            pass
        close_voice_quick_card_window(app)
        try:
            if parent.winfo_exists():
                parent.lift()
                entry = getattr(app, "quick_caption_entry", None)
                if entry is not None:
                    entry.focus_set()
        except Exception:
            pass
        if callable(on_finished):
            on_finished()

    app.voice_quick_card_finish = finish_with_text

    try:
        window = ctk.CTkToplevel(parent)
        app.voice_quick_card_window = window
        window.title("Voice Quick Card – Auswahl")
        window.minsize(580, 400)
        window.transient(parent)
        window.protocol(
            "WM_DELETE_WINDOW",
            lambda: finish_with_text(
                query.strip(), "VOICE QUICK CARD CLOSED · dictation kept"
            ),
        )
        window.bind(
            "<Escape>",
            lambda _event: finish_with_text(
                query.strip(), "VOICE QUICK CARD CLOSED · dictation kept"
            ),
        )

        header = ctk.CTkFrame(window, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(
            header,
            text="VOICE QUICK CARD",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(
            header,
            text="SCHLIESSEN",
            width=110,
            command=lambda: finish_with_text(
                query.strip(), "VOICE QUICK CARD CLOSED · dictation kept"
            ),
        ).pack(side="right")

        ctk.CTkLabel(
            window,
            text=f"Gesprochen: {query.strip()}",
            anchor="w",
            justify="left",
            wraplength=620,
        ).pack(fill="x", padx=22, pady=(0, 10))

        if matches:
            ctk.CTkLabel(
                window,
                text=(
                    "Wähle mit der Maus oder sage: "
                    "Vadafok One / Two / Three (oder Eins / Zwei / Drei)"
                ),
                anchor="w",
                justify="left",
                wraplength=620,
            ).pack(fill="x", padx=22, pady=(0, 8))

            for index, match in enumerate(matches, start=1):
                button_text = (
                    f"{index}  ·  {match.text}\n"
                    f"Kategorie: {match.category}   ·   Treffer: {match.score:.0%}"
                )
                ctk.CTkButton(
                    window,
                    text=button_text,
                    anchor="w",
                    height=70,
                    command=lambda number=index: select_voice_quick_card(app, number),
                ).pack(fill="x", padx=22, pady=5)
        else:
            ctk.CTkLabel(
                window,
                text="Keine ausreichend passende Quick Card gefunden.",
                font=ctk.CTkFont(size=17, weight="bold"),
                anchor="w",
            ).pack(fill="x", padx=22, pady=(18, 6))
            ctk.CTkLabel(
                window,
                text=(
                    "Der erkannte Satz bleibt erhalten. Klicke unten oder sage "
                    "Vadafok Text, um ihn als freie Caption zu verwenden."
                ),
                anchor="w",
                justify="left",
                wraplength=620,
            ).pack(fill="x", padx=22, pady=(0, 16))

        ctk.CTkButton(
            window,
            text="ERKANNTEN TEXT VERWENDEN (KEINE QUICK CARD)",
            command=lambda: use_recognized_voice_quick_card_text(app),
        ).pack(fill="x", padx=22, pady=(14, 8))

        available_commands = []
        english_numbers = ("Vadafok One", "Vadafok Two", "Vadafok Three")
        german_numbers = ("Eins", "Zwei", "Drei")
        for index in range(len(matches)):
            available_commands.append(
                f"{english_numbers[index]} / {german_numbers[index]}"
            )
        available_commands.extend(("Vadafok Text", "Vadafok Back", "Vadafok Stop"))
        add_voice_help(
            window,
            available_commands,
            state_text="Waiting for Quick Card selection",
            attribute_name="_vadafok_quick_card_voice_help",
        )

        def monitor_parent() -> None:
            try:
                if not window.winfo_exists():
                    return
                if not parent.winfo_exists():
                    close_voice_quick_card_window(app)
                    return
                window.after(250, monitor_parent)
            except Exception:
                close_voice_quick_card_window(app)

        _position_near_parent(window, parent)
        window.after(0, window.lift)
        window.after(30, window.focus_force)
        window.after(250, monitor_parent)
        return True

    except Exception as exc:
        close_voice_quick_card_window(app)
        app.voice_quick_card_mode = False
        try:
            app.voice_status_var.set(f"VOICE QUICK CARD ERROR · {str(exc)[:90]}")
        except Exception:
            pass
        replace_quick_caption_text(app, query.strip())
        if callable(on_finished):
            on_finished()
        return False
