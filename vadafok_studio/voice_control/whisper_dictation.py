"""Local Whisper dictation for VADAFOK Studio.

Windows System.Speech remains responsible for the small command grammar.
This module records free speech locally and transcribes it with faster-whisper.
No audio is sent to OBS or to an online service.
"""

from __future__ import annotations

import json
import math
import threading
import time
from pathlib import Path
from typing import Any, Callable

_CONFIG_PATH = Path(__file__).with_name("whisper_settings.json")
_MODEL_LOCK = threading.Lock()
_MODEL: Any = None
_MODEL_KEY: tuple[str, str, str] | None = None


def _load_config() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "model": "small",
        "device": "cpu",
        "compute_type": "int8",
        "sample_rate": 16000,
        "speech_threshold": 0.012,
        "silence_seconds": 1.0,
        "minimum_speech_seconds": 0.35,
        "maximum_phrase_seconds": 18.0,
        "beam_size": 5,
    }
    try:
        data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            defaults.update(data)
    except Exception:
        pass
    return defaults


def _language_for_app(app: Any) -> str | None:
    for name in ("voice_recognition_culture", "voice_culture_var"):
        value = getattr(app, name, None)
        try:
            culture = str(value.get()).strip().lower()
        except Exception:
            continue
        if culture.startswith("de"):
            return "de"
        if culture.startswith("en"):
            return "en"
    return None


def _get_model(config: dict[str, Any], on_status: Callable[[str], None]) -> Any:
    global _MODEL, _MODEL_KEY

    model_name = str(config.get("model", "small"))
    device = str(config.get("device", "cpu"))
    compute_type = str(config.get("compute_type", "int8"))
    key = (model_name, device, compute_type)

    with _MODEL_LOCK:
        if _MODEL is not None and _MODEL_KEY == key:
            return _MODEL

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper fehlt. Bitte INSTALL_VOICE_DEPENDENCIES.bat ausführen."
            ) from exc

        on_status(
            f"WHISPER MODEL · loading {model_name} ({device}/{compute_type})"
        )
        _MODEL = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
        )
        _MODEL_KEY = key
        return _MODEL


def _rms(block: Any) -> float:
    # numpy is imported lazily so VADAFOK can still start before dependencies
    # are installed and can show a useful error in the Settings page.
    import numpy as np

    values = np.asarray(block, dtype=np.float32).reshape(-1)
    if values.size == 0:
        return 0.0
    return float(math.sqrt(float(np.mean(values * values))))


class WhisperDictationSession:
    def __init__(
        self,
        app: Any,
        on_text: Callable[[str], None],
        on_status: Callable[[str], None],
    ) -> None:
        self.app = app
        self.on_text = on_text
        self.on_status = on_status
        self.stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self._run,
            name="VADAFOK-Whisper-Dictation",
            daemon=True,
        )

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()

    def _run(self) -> None:
        try:
            import numpy as np
            import sounddevice as sd
        except ImportError:
            self.on_status(
                "WHISPER ERROR · dependencies missing · run INSTALL_VOICE_DEPENDENCIES.bat"
            )
            return

        config = _load_config()
        try:
            model = _get_model(config, self.on_status)
        except Exception as exc:
            self.on_status(f"WHISPER ERROR · {str(exc)[:105]}")
            return

        sample_rate = int(config.get("sample_rate", 16000))
        block_size = max(320, int(sample_rate * 0.10))
        threshold = float(config.get("speech_threshold", 0.012))
        silence_seconds = float(config.get("silence_seconds", 1.0))
        minimum_seconds = float(config.get("minimum_speech_seconds", 0.35))
        maximum_seconds = float(config.get("maximum_phrase_seconds", 18.0))
        required_silent_blocks = max(1, int(silence_seconds * sample_rate / block_size))
        minimum_samples = int(minimum_seconds * sample_rate)
        maximum_samples = int(maximum_seconds * sample_rate)

        self.on_status("WHISPER READY · speak your caption")

        try:
            with sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
                blocksize=block_size,
            ) as stream:
                while not self.stop_event.is_set():
                    frames: list[Any] = []
                    speech_started = False
                    silent_blocks = 0

                    while not self.stop_event.is_set():
                        block, overflowed = stream.read(block_size)
                        if overflowed:
                            self.on_status("WHISPER WARNING · microphone buffer overflow")

                        level = _rms(block)
                        if not speech_started:
                            if level >= threshold:
                                speech_started = True
                                frames.append(block.copy())
                                self.on_status("WHISPER LISTENING · recording phrase")
                            continue

                        frames.append(block.copy())
                        if level < threshold:
                            silent_blocks += 1
                        else:
                            silent_blocks = 0

                        sample_count = sum(len(item) for item in frames)
                        if silent_blocks >= required_silent_blocks:
                            break
                        if sample_count >= maximum_samples:
                            break

                    if self.stop_event.is_set():
                        break
                    if not frames:
                        continue

                    audio = np.concatenate(frames, axis=0).reshape(-1)
                    if audio.size < minimum_samples:
                        continue

                    self.on_status("WHISPER TRANSCRIBING · please wait")
                    language = _language_for_app(self.app)
                    segments, info = model.transcribe(
                        audio,
                        language=language,
                        beam_size=int(config.get("beam_size", 5)),
                        vad_filter=True,
                        condition_on_previous_text=False,
                        initial_prompt=(
                            "VADAFOK, OBS, Quick Card, Intertitel, silent stream, "
                            "Thank you for the follow, Chat was right"
                        ),
                    )
                    text = " ".join(segment.text.strip() for segment in segments).strip()
                    if text:
                        self.on_text(text)
                    self.on_status("WHISPER READY · speak or say VADAFOK SHOW")
        except Exception as exc:
            self.on_status(f"WHISPER ERROR · {str(exc)[:105]}")


def start_whisper_dictation(
    app: Any,
    *,
    on_text: Callable[[str], None],
    on_status: Callable[[str], None],
) -> None:
    stop_whisper_dictation(app)
    session = WhisperDictationSession(app, on_text, on_status)
    setattr(app, "_vadafok_whisper_session", session)
    session.start()


def stop_whisper_dictation(app: Any) -> None:
    session = getattr(app, "_vadafok_whisper_session", None)
    if session is not None:
        try:
            session.stop()
        except Exception:
            pass
    setattr(app, "_vadafok_whisper_session", None)
