"""Translation support for the compact F8 Live Card workflow.

Whisper keeps the dictated German text active in the existing Quick Caption
textbox. An English preview is prepared asynchronously and shown inside the
same small window. Only VADAFOK ENGLISH replaces the active textbox content.
"""
from __future__ import annotations

import threading
from typing import Any

from vadafok_studio.translator.runtime import translate_text


def _set_preview(app: Any, text: str, state: str = "") -> None:
    app.live_card_translation_state = state
    app.live_card_translation_preview = str(text or "").strip()
    label = getattr(app, "quick_caption_translation_label", None)
    if label is not None:
        try:
            label.configure(text=str(text or ""))
        except Exception:
            pass


def reset_live_card_translation(app: Any) -> None:
    app.live_card_original_text = ""
    app.live_card_translation_preview = ""
    app.live_card_translation_state = ""
    app.live_card_translation_request_id = int(
        getattr(app, "live_card_translation_request_id", 0) or 0
    ) + 1
    _set_preview(app, "Speak to prepare English…", "idle")


def prepare_live_card_translation(app: Any, original_text: str) -> None:
    original = str(original_text or "").strip()
    if not original:
        reset_live_card_translation(app)
        return

    app.live_card_original_text = original
    request_id = int(getattr(app, "live_card_translation_request_id", 0) or 0) + 1
    app.live_card_translation_request_id = request_id
    _set_preview(app, "Translating…", "loading")

    def worker() -> None:
        result = translate_text(original, target_language="EN")

        def finish() -> None:
            if request_id != getattr(app, "live_card_translation_request_id", None):
                return
            translated = str(getattr(result, "translated_text", "") or "").strip()
            if result.success and translated:
                _set_preview(app, translated, "ready")
                try:
                    app.voice_status_var.set(
                        "F8 TRANSLATION READY · say VADAFOK ENGLISH if needed"
                    )
                except Exception:
                    pass
            else:
                message = str(getattr(result, "error", "") or "Translation unavailable").strip()
                _set_preview(app, f"Translation unavailable · {message[:70]}", "error")

        try:
            app.after(0, finish)
        except Exception:
            pass

    threading.Thread(
        target=worker,
        name="VADAFOK-F8-Live-Card-Translation",
        daemon=True,
    ).start()


def _replace_quick_caption_text(app: Any, text: str) -> bool:
    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        return False
    try:
        entry.delete("1.0", "end")
        entry.insert("1.0", str(text or "").strip())
        entry.mark_set("insert", "end")
        entry.see("end")
        entry.focus_set()
        return True
    except Exception:
        return False


def use_live_card_translation(app: Any) -> bool:
    translated = str(getattr(app, "live_card_translation_preview", "") or "").strip()
    if getattr(app, "live_card_translation_state", "") != "ready" or not translated:
        return False
    return _replace_quick_caption_text(app, translated)


def restore_live_card_original(app: Any) -> bool:
    original = str(getattr(app, "live_card_original_text", "") or "").strip()
    if not original:
        return False
    return _replace_quick_caption_text(app, original)
