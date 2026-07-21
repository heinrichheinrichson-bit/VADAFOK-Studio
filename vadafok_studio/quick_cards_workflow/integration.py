"""Quick Cards Workflow RC1: favorites, recent cards, and fast search.

Installed as a runtime extension so the large app.py stays untouched.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from ..core.window_icon import apply_window_icon

_INSTALLED = False
_ROOT = Path(__file__).resolve().parents[2]
_STATE_PATH = _ROOT / "data" / "quick_cards_workflow.json"
_LIBRARY_PATH = _ROOT / "text_library.json"


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _save_state(state: dict[str, list[str]]) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _state() -> dict[str, list[str]]:
    raw = _load_json(_STATE_PATH, {})
    return {
        "favorites": list(dict.fromkeys(str(x) for x in raw.get("favorites", []) if str(x).strip()))[:30],
        "recent": list(dict.fromkeys(str(x) for x in raw.get("recent", []) if str(x).strip()))[:10],
    }


def _cards() -> list[tuple[str, str]]:
    data = _load_json(_LIBRARY_PATH, {})
    result: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for category, values in data.items():
            if isinstance(values, list):
                result.extend((str(category), str(v).strip()) for v in values if str(v).strip())
    return result


def _use_card(app: Any, text: str) -> None:
    state = _state()
    state["recent"] = [text] + [x for x in state["recent"] if x != text]
    state["recent"] = state["recent"][:10]
    _save_state(state)
    try:
        app.live_card_pending_text = text
        app.show_live_card()
    except Exception:
        try:
            app.open_quick_caption()
            app.after(100, lambda: _fill_quick_caption(app, text))
        except Exception:
            pass


def _fill_quick_caption(app: Any, text: str) -> None:
    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        return
    try:
        entry.delete("1.0", "end")
        entry.insert("1.0", text)
        entry.focus_set()
    except Exception:
        pass


def _open_workflow(app: Any) -> None:
    try:
        import customtkinter as ctk
    except Exception:
        return
    old = getattr(app, "quick_cards_workflow_window", None)
    try:
        if old is not None and old.winfo_exists():
            old.lift(); old.focus_force(); return
    except Exception:
        pass

    window = ctk.CTkToplevel(app)
    apply_window_icon(window, app)
    app.quick_cards_workflow_window = window
    window.title("Quick Cards Workflow")
    window.geometry("860x620")
    window.minsize(700, 500)
    window.transient(app)
    window.protocol("WM_DELETE_WINDOW", window.destroy)
    window.bind("<Escape>", lambda _e: window.destroy())

    state = _state()
    search_var = ctk.StringVar(value="")
    mode_var = ctk.StringVar(value="Favorites")

    header = ctk.CTkFrame(window, fg_color="transparent")
    header.pack(fill="x", padx=18, pady=(16, 8))
    ctk.CTkLabel(header, text="QUICK CARDS WORKFLOW", font=ctk.CTkFont(size=22, weight="bold"), text_color="#D6A43A").pack(side="left")
    ctk.CTkButton(header, text="CLOSE", width=90, command=window.destroy).pack(side="right")

    controls = ctk.CTkFrame(window, fg_color="#111111")
    controls.pack(fill="x", padx=18, pady=(0, 10))
    search = ctk.CTkEntry(controls, textvariable=search_var, placeholder_text="Search Quick Cards…")
    search.pack(side="left", fill="x", expand=True, padx=10, pady=10)
    for name in ("Favorites", "Recent", "All"):
        ctk.CTkButton(controls, text=name.upper(), width=90, command=lambda n=name: (mode_var.set(n), render())).pack(side="left", padx=(0, 8), pady=10)

    info = ctk.CTkLabel(window, text="", text_color="#BCA870")
    info.pack(anchor="w", padx=22)
    body = ctk.CTkScrollableFrame(window, fg_color="#0B0B0B")
    body.pack(fill="both", expand=True, padx=18, pady=(6, 16))

    def toggle(text: str) -> None:
        current = _state()
        favs = current["favorites"]
        current["favorites"] = [x for x in favs if x != text] if text in favs else [text] + favs
        current["favorites"] = current["favorites"][:30]
        _save_state(current)
        render()

    def render(*_args: Any) -> None:
        for child in body.winfo_children(): child.destroy()
        current = _state(); all_cards = _cards(); by_text = {text: cat for cat, text in all_cards}
        mode = mode_var.get(); query = search_var.get().strip().casefold()
        if mode == "Favorites": texts = current["favorites"]
        elif mode == "Recent": texts = current["recent"]
        else: texts = [text for _cat, text in all_cards]
        if query: texts = [t for t in texts if query in t.casefold() or query in by_text.get(t, "").casefold()]
        info.configure(text=f"{mode}: {len(texts)} cards")
        if not texts:
            ctk.CTkLabel(body, text="No cards here yet.", text_color="#BCA870").pack(anchor="w", padx=14, pady=18)
            return
        for text in texts:
            row = ctk.CTkFrame(body, fg_color="#151515", corner_radius=10)
            row.pack(fill="x", padx=8, pady=5)
            fav = text in current["favorites"]
            ctk.CTkButton(row, text="★" if fav else "☆", width=42, fg_color="#8A641D" if fav else "#333333", command=lambda t=text: toggle(t)).pack(side="left", padx=8, pady=8)
            button = ctk.CTkButton(row, text=text, anchor="w", fg_color="transparent", hover_color="#2A2A2A", command=lambda t=text: (_use_card(app, t), window.destroy()))
            button.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=8)
            ctk.CTkLabel(row, text=by_text.get(text, ""), text_color="#8F8058", width=100).pack(side="right", padx=10)

    search_var.trace_add("write", render)
    render()
    search.focus_set()


def install_quick_cards_workflow() -> None:
    global _INSTALLED
    if _INSTALLED: return
    _INSTALLED = True
    from vadafok_studio.app import VadafokStudio
    original = VadafokStudio.show_quick_cards

    def wrapped(self: Any, *args: Any, **kwargs: Any):
        result = original(self, *args, **kwargs)
        try:
            button = __import__("customtkinter").CTkButton(
                self.main, text="★ FAVORITES / RECENT", width=190,
                fg_color="#D6A43A", text_color="#111111", hover_color="#8A641D",
                command=lambda: _open_workflow(self),
            )
            button.place(relx=1.0, x=-28, y=24, anchor="ne")
        except Exception:
            pass
        return result

    VadafokStudio.show_quick_cards = wrapped
