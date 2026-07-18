"""Local WAV sound discovery and playback for VADAFOK Studio.

The service deliberately has no GUI or OBS dependency.  Paths exposed by the
public API are relative to ``<project>/Sounds`` so callers can persist them
without tying configuration to one machine.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable


class SoundService:
    """Discover and play WAV files from a project's ``Sounds`` directory."""

    SOUND_DIRECTORY_NAME = "Sounds"
    SUPPORTED_SUFFIXES = frozenset({".wav"})

    def __init__(self, project_dir: str | os.PathLike[str] | None = None, *, backend: Any = None):
        self._project_dir = self._normalize_project_dir(project_dir)
        self._backend = backend if backend is not None else self._load_default_backend()
        self._sounds: list[str] = []

    @staticmethod
    def _normalize_project_dir(project_dir: str | os.PathLike[str] | None) -> Path | None:
        if project_dir is None:
            return None
        try:
            return Path(project_dir).expanduser().resolve(strict=False)
        except (OSError, RuntimeError, TypeError, ValueError):
            return None

    @staticmethod
    def _load_default_backend() -> Any:
        """Load winsound lazily; return ``None`` on unsupported platforms."""
        try:
            import winsound  # type: ignore[import-not-found]
        except (ImportError, OSError):
            return None
        return winsound

    @property
    def project_dir(self) -> Path | None:
        return self._project_dir

    @property
    def sounds_dir(self) -> Path | None:
        if self._project_dir is None:
            return None
        return self._project_dir / self.SOUND_DIRECTORY_NAME

    def set_project_dir(self, project_dir: str | os.PathLike[str] | None) -> list[str]:
        """Change the active project and immediately refresh the sound list."""
        self.stop()
        self._project_dir = self._normalize_project_dir(project_dir)
        return self.scan()

    def scan(self) -> list[str]:
        """Scan ``<project>/Sounds`` recursively and return sorted relative paths."""
        root = self.sounds_dir
        if root is None or not root.is_dir():
            self._sounds = []
            return []

        found: list[str] = []
        try:
            candidates: Iterable[Path] = root.rglob("*")
            for candidate in candidates:
                try:
                    if candidate.is_file() and candidate.suffix.lower() in self.SUPPORTED_SUFFIXES:
                        found.append(candidate.relative_to(root).as_posix())
                except (OSError, RuntimeError, ValueError):
                    continue
        except (OSError, RuntimeError):
            found = []

        self._sounds = sorted(set(found), key=lambda value: (value.casefold(), value))
        return list(self._sounds)

    def list_sounds(self, *, refresh: bool = False) -> list[str]:
        """Return a copy of the known sound paths, optionally rescanning first."""
        if refresh:
            return self.scan()
        return list(self._sounds)

    def resolve(self, sound_path: str | os.PathLike[str] | None) -> Path | None:
        """Resolve a relative sound path while preventing escape from ``Sounds``."""
        root = self.sounds_dir
        if root is None or sound_path is None:
            return None

        try:
            raw = Path(sound_path).expanduser()
            candidate = raw.resolve(strict=False) if raw.is_absolute() else (root / raw).resolve(strict=False)
            root_resolved = root.resolve(strict=False)
            candidate.relative_to(root_resolved)
        except (OSError, RuntimeError, TypeError, ValueError):
            return None

        if candidate.suffix.lower() not in self.SUPPORTED_SUFFIXES:
            return None
        return candidate

    def exists(self, sound_path: str | os.PathLike[str] | None) -> bool:
        """Return whether *sound_path* is a valid WAV file inside ``Sounds``."""
        candidate = self.resolve(sound_path)
        if candidate is None:
            return False
        try:
            return candidate.is_file()
        except OSError:
            return False

    def play(self, sound_path: str | os.PathLike[str] | None) -> bool:
        """Play a WAV asynchronously; return ``False`` instead of raising errors."""
        candidate = self.resolve(sound_path)
        backend = self._backend
        if candidate is None or backend is None or not self.exists(candidate):
            return False

        try:
            flags = int(getattr(backend, "SND_FILENAME", 0)) | int(getattr(backend, "SND_ASYNC", 0))
            no_default = getattr(backend, "SND_NODEFAULT", None)
            if no_default is not None:
                flags |= int(no_default)
            backend.PlaySound(str(candidate), flags)
            return True
        except (OSError, RuntimeError, TypeError, ValueError):
            return False

    def stop(self) -> bool:
        """Stop current playback; unsupported backends fail safely."""
        backend = self._backend
        if backend is None:
            return False
        try:
            backend.PlaySound(None, 0)
            return True
        except (OSError, RuntimeError, TypeError, ValueError):
            return False
