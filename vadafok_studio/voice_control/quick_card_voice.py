"""Safe voice-assisted Quick Card search for VADAFOK Studio.

The Quick Card library is read-only. All Tk/CustomTkinter UI work happens on
Tk's main thread. Suggestions can be selected by mouse or fixed voice commands.
The recognized text is translated asynchronously while the result window stays
open, so existing Quick Card selection remains responsive.
"""

from __future__ import annotations

import json
import re
import threading
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable

from .voice_help import add_voice_help
from ..core.window_icon import apply_window_icon


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_CANDIDATES = (
    _PROJECT_ROOT / "text_library.json",
    _PROJECT_ROOT / "docs" / "text_library.json",
)
_MIN_SUGGESTION_SCORE = 0.60
_DEFAULT_TARGET_LANGUAGE = "EN"
_TRANSLATION_TIMEOUT_SECONDS = 5.0


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
    app.voice_quick_card_translation = ""
    app.voice_quick_card_translation_state = ""
    app.voice_quick_card_translation_error = ""
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
        ww, wh = max(window.winfo_reqwidth(), 660), max(window.winfo_reqheight(), 500)

        x = px + pw + 16
        y = py
        if x + ww > sw - 20:
            x = px
            y = py + ph + 16
        x = max(20, min(x, sw - ww - 20))
        y = max(20, min(y, sh - wh - 60))
        window.geometry(f"{ww}x{wh}+{x}+{y}")
    except Exception:
        window.geometry("680x500")


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


def use_translated_voice_quick_card_text(app: Any) -> bool:
    """Use the prepared translation only while the result window is open."""

    if not voice_quick_card_window_is_open(app):
        return False
    translated = str(
        getattr(app, "voice_quick_card_translation", "") or ""
    ).strip()
    callback = getattr(app, "voice_quick_card_finish", None)
    if not translated or not callable(callback):
        return False
    callback(translated, "TRANSLATION USED · say VADAFOK SHOW")
    return True


def _translation_target_language(app: Any) -> str:
    """Read an optional app/config override; default to English."""

    try:
        config = getattr(app, "config_data", {}) or {}
        value = str(config.get("translation_target_language", "") or "").strip()
        if value:
            return value.upper()
    except Exception:
        pass
    return _DEFAULT_TARGET_LANGUAGE


def _start_translation(
    app: Any,
    query: str,
    translation_label: Any,
    translate_button: Any,
) -> None:
    """Prepare the DeepL translation without blocking Tk."""

    app.voice_quick_card_translation = ""
    app.voice_quick_card_translation_error = ""
    app.voice_quick_card_translation_state = "loading"

    def update_ui(text: str, button_state: str = "disabled") -> None:
        try:
            if voice_quick_card_window_is_open(app):
                translation_label.configure(text=text)
                translate_button.configure(state=button_state)
        except Exception:
            pass

    def worker() -> None:
        try:
            from vadafok_studio.translator.runtime import translate_text

            result = translate_text(
                query,
                source_language="",
                target_language=_translation_target_language(app),
            )
            if not result.success or not result.translated_text.strip():
                raise RuntimeError(result.error or "Keine Übersetzung erhalten.")

            translated = result.translated_text.strip()

            def success() -> None:
                if not voice_quick_card_window_is_open(app):
                    return
                app.voice_quick_card_translation = translated
                app.voice_quick_card_translation_state = "ready"
                app.voice_quick_card_translation_error = ""
                update_ui(
                    f"Übersetzung:\n{translated}\n\n"
                    "Sprachbefehl: VADAFOK ENGLISH",
                    "normal",
                )

            app.after(0, success)
        except Exception as exc:
            error = str(exc).strip() or "Unbekannter Übersetzungsfehler"

            def failure() -> None:
                if not voice_quick_card_window_is_open(app):
                    return
                app.voice_quick_card_translation = ""
                app.voice_quick_card_translation_state = "error"
                app.voice_quick_card_translation_error = error
                update_ui(
                    "Übersetzung momentan nicht verfügbar.\n"
                    "Technische Details: logs/translation.log",
                    "disabled",
                )

            app.after(0, failure)

    threading.Thread(
        target=worker,
        name="VADAFOK-QuickCard-Translation",
        daemon=True,
    ).start()


def show_quick_card_matches(
    app: Any,
    query: str,
    on_finished: Callable[[], None] | None = None,
) -> bool:
    """Show Quick Card matches and prepare a translation suggestion."""

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
    app.voice_quick_card_translation = ""
    app.voice_quick_card_translation_state = "loading"
    app.voice_quick_card_translation_error = ""
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
        apply_window_icon(window, parent)
        app.voice_quick_card_window = window
        window.title("Voice Quick Card – Auswahl")
        window.minsize(580, 470)
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
                    "Sage VADAFOK ONE / TWO / THREE für eine Quick Card, "
                    "VADAFOK TEXT für den erkannten Satz oder "
                    "VADAFOK ENGLISH für die Übersetzung."
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
                    "Der erkannte Satz bleibt sichtbar. Sage VADAFOK TEXT oder, "
                    "sobald sie bereit ist, VADAFOK ENGLISH."
                ),
                anchor="w",
                justify="left",
                wraplength=620,
            ).pack(fill="x", padx=22, pady=(0, 12))

        translation_frame = ctk.CTkFrame(window)
        translation_frame.pack(fill="x", padx=22, pady=(10, 6))
        translation_label = ctk.CTkLabel(
            translation_frame,
            text="Übersetzung wird vorbereitet …",
            anchor="w",
            justify="left",
            wraplength=600,
        )
        translation_label.pack(fill="x", padx=14, pady=(12, 8))

        translate_button = ctk.CTkButton(
            translation_frame,
            text="ÜBERSETZUNG VERWENDEN · VADAFOK ENGLISH",
            state="disabled",
            command=lambda: use_translated_voice_quick_card_text(app),
        )
        translate_button.pack(fill="x", padx=14, pady=(0, 12))

        ctk.CTkButton(
            window,
            text="ERKANNTEN TEXT VERWENDEN · VADAFOK TEXT",
            command=lambda: use_recognized_voice_quick_card_text(app),
        ).pack(fill="x", padx=22, pady=(8, 8))

        available_commands = []
        english_numbers = ("Vadafok One", "Vadafok Two", "Vadafok Three")
        german_numbers = ("Eins", "Zwei", "Drei")
        for index in range(len(matches)):
            available_commands.append(
                f"{english_numbers[index]} / {german_numbers[index]}"
            )
        available_commands.extend(
            (
                "Vadafok Text",
                "Vadafok English",
                "Vadafok Translate (Alias)",
                "Vadafok Back",
                "Vadafok Stop",
            )
        )
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
        _start_translation(app, query.strip(), translation_label, translate_button)
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
