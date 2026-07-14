"""Voice-control extensions for VADAFOK Studio."""

from .foundation import install_voice_foundation as _install_foundation
from .language_selection import install_language_selection


def install_voice_foundation() -> None:
    """Install the existing voice foundation and the language selector."""
    _install_foundation()
    install_language_selection()


__all__ = ["install_voice_foundation"]
