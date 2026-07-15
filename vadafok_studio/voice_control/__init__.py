"""Voice-control and workflow extensions for VADAFOK Studio."""
from .foundation import install_voice_foundation as _install_foundation
from .language_selection import install_language_selection


def install_voice_foundation() -> None:
    _install_foundation()
    install_language_selection()

    try:
        from vadafok_studio.quick_cards_workflow import install_quick_cards_workflow
        install_quick_cards_workflow()
    except Exception as exc:
        print(f"[Quick Cards Workflow] not installed: {exc}")

    try:
        from vadafok_studio.banner_workflow import install_banner_workflow
        install_banner_workflow()
    except Exception as exc:
        print(f"[Banner Workflow] not installed: {exc}")

    try:
        from vadafok_studio.stream_workflow import install_stream_workflow
        install_stream_workflow()
    except Exception as exc:
        print(f"[Stream Workflow] not installed: {exc}")


__all__ = ["install_voice_foundation"]
