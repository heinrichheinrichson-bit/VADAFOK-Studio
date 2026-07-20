"""Voice-control and workflow extensions for VADAFOK Studio.

Imports are intentionally lazy so non-GUI modules and unit tests can use the
voice package without requiring CustomTkinter at import time.
"""

from __future__ import annotations


def install_voice_foundation() -> None:
    from .foundation import install_voice_foundation as install_foundation
    from .language_selection import install_language_selection

    install_foundation()
    install_language_selection()

    optional_installers = (
        ("vadafok_studio.quick_cards_workflow", "install_quick_cards_workflow", "Quick Cards Workflow"),
        ("vadafok_studio.banner_workflow", "install_banner_workflow", "Banner Workflow"),
        ("vadafok_studio.stream_workflow", "install_stream_workflow", "Stream Workflow"),
        ("vadafok_studio.card_creator_obs", "install_card_creator_obs_display", "Card Creator OBS"),
    )

    for module_name, function_name, label in optional_installers:
        try:
            module = __import__(module_name, fromlist=[function_name])
            getattr(module, function_name)()
        except Exception as exc:
            print(f"[{label}] not installed: {exc}")


__all__ = ["install_voice_foundation"]
