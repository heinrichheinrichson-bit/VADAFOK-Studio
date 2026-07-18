import tempfile
import unittest
from pathlib import Path

from vadafok_studio.services.sound_service import SoundService


class FakeBackend:
    SND_FILENAME = 1
    SND_ASYNC = 2
    SND_NODEFAULT = 4

    def __init__(self, error=None):
        self.calls = []
        self.error = error

    def PlaySound(self, path, flags):
        if self.error is not None:
            raise self.error
        self.calls.append((path, flags))


class SoundServiceTests(unittest.TestCase):
    def test_missing_project_or_sounds_folder_returns_empty_list(self):
        self.assertEqual(SoundService().scan(), [])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(SoundService(tmp).scan(), [])

    def test_scan_is_recursive_wav_only_and_case_insensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Sounds"
            (root / "Hype").mkdir(parents=True)
            (root / "z.wav").write_bytes(b"wav")
            (root / "Hype" / "Airhorn.WAV").write_bytes(b"wav")
            (root / "ignore.mp3").write_bytes(b"mp3")

            service = SoundService(tmp)
            self.assertEqual(service.scan(), ["Hype/Airhorn.WAV", "z.wav"])
            self.assertEqual(service.list_sounds(), ["Hype/Airhorn.WAV", "z.wav"])

    def test_list_sounds_returns_copy_and_refreshes_on_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Sounds"
            root.mkdir()
            (root / "one.wav").write_bytes(b"wav")
            service = SoundService(tmp)
            values = service.scan()
            values.append("modified.wav")
            self.assertEqual(service.list_sounds(), ["one.wav"])
            (root / "two.wav").write_bytes(b"wav")
            self.assertEqual(service.list_sounds(refresh=True), ["one.wav", "two.wav"])

    def test_resolve_exists_and_path_escape_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            sounds = project / "Sounds"
            sounds.mkdir()
            valid = sounds / "ok.wav"
            valid.write_bytes(b"wav")
            outside = project / "outside.wav"
            outside.write_bytes(b"wav")
            service = SoundService(project)

            self.assertEqual(service.resolve("ok.wav"), valid.resolve())
            self.assertTrue(service.exists("ok.wav"))
            self.assertFalse(service.exists("missing.wav"))
            self.assertIsNone(service.resolve("../outside.wav"))
            self.assertIsNone(service.resolve(outside))
            self.assertIsNone(service.resolve("not-a-wave.mp3"))

    def test_play_uses_async_filename_backend_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            sound = Path(tmp) / "Sounds" / "ping.wav"
            sound.parent.mkdir()
            sound.write_bytes(b"wav")
            backend = FakeBackend()
            service = SoundService(tmp, backend=backend)

            self.assertTrue(service.play("ping.wav"))
            self.assertEqual(backend.calls, [(str(sound.resolve()), 7)])

    def test_play_and_stop_fail_safely(self):
        with tempfile.TemporaryDirectory() as tmp:
            sound = Path(tmp) / "Sounds" / "ping.wav"
            sound.parent.mkdir()
            sound.write_bytes(b"wav")

            self.assertFalse(SoundService(tmp, backend=None).play("missing.wav"))
            broken = SoundService(tmp, backend=FakeBackend(OSError("audio error")))
            self.assertFalse(broken.play("ping.wav"))
            self.assertFalse(broken.stop())

    def test_stop_calls_backend(self):
        backend = FakeBackend()
        service = SoundService(backend=backend)
        self.assertTrue(service.stop())
        self.assertEqual(backend.calls, [(None, 0)])

    def test_set_project_dir_stops_and_rescans(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_sound = Path(first) / "Sounds" / "first.wav"
            second_sound = Path(second) / "Sounds" / "second.wav"
            first_sound.parent.mkdir()
            second_sound.parent.mkdir()
            first_sound.write_bytes(b"wav")
            second_sound.write_bytes(b"wav")
            backend = FakeBackend()
            service = SoundService(first, backend=backend)
            service.scan()

            self.assertEqual(service.set_project_dir(second), ["second.wav"])
            self.assertEqual(backend.calls, [(None, 0)])


if __name__ == "__main__":
    unittest.main()
