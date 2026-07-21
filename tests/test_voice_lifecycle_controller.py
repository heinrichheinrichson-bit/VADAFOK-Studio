import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.voice_control.lifecycle import VoiceLifecycleController


class Variable:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class VoiceLifecycleControllerTests(unittest.TestCase):
    def make_app(self):
        return SimpleNamespace(
            voice_status_var=Variable(),
            voice_culture=Variable("de-DE"),
            voice_enabled=Variable(True),
            voice_last_heard_var=Variable(),
            voice_process=None,
            voice_reader_thread=None,
            voice_stop_requested=False,
            voice_reader_loop=Mock(),
            save_config=Mock(),
            after=Mock(),
            open_quick_caption=Mock(),
            destroy=Mock(),
        )

    @patch("vadafok_studio.voice_control.lifecycle.sys.platform", "linux")
    def test_start_reports_unsupported_platform_without_process(self):
        app = self.make_app()
        VoiceLifecycleController(app).start()
        self.assertEqual(app.voice_status_var.get(), "WINDOWS ONLY")
        self.assertIsNone(app.voice_process)

    def test_start_is_idempotent_while_listener_is_running(self):
        app = self.make_app()
        app.voice_process = Mock()
        app.voice_process.poll.return_value = None
        controller = VoiceLifecycleController(app)
        with patch("vadafok_studio.voice_control.lifecycle.sys.platform", "win32"):
            controller.start()
        self.assertEqual(app.voice_status_var.get(), "LISTENING")

    def test_stop_terminates_process_and_joins_reader(self):
        app = self.make_app()
        process = Mock()
        thread = Mock()
        app.voice_process = process
        app.voice_reader_thread = thread
        VoiceLifecycleController(app).stop()
        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=1.2)
        thread.join.assert_called_once_with(timeout=0.35)
        self.assertIsNone(app.voice_process)
        self.assertIsNone(app.voice_reader_thread)
        self.assertTrue(app.voice_stop_requested)
        self.assertEqual(app.voice_status_var.get(), "OFF")

    def test_close_stops_voice_before_destroying_app(self):
        app = self.make_app()
        controller = VoiceLifecycleController(app)
        controller.close_app()
        self.assertEqual(app.voice_status_var.get(), "OFF")
        app.destroy.assert_called_once()

    def test_reader_dispatches_ready_and_heard_protocol(self):
        app = self.make_app()
        process = Mock()
        process.stdout.readline.side_effect = [
            "__READY__|de-DE|Desktop microphone\n",
            "__HEARD__|0.95|command|live card\n",
            "",
        ]
        process.poll.return_value = 0
        VoiceLifecycleController(app).reader_loop(process)
        self.assertEqual(app.after.call_count, 3)  # ready, heard, stopped

    def test_reader_error_does_not_overwrite_error_with_stopped(self):
        app = self.make_app()
        process = Mock()
        process.stdout.readline.side_effect = ["__ERROR__|microphone missing\n", ""]
        VoiceLifecycleController(app).reader_loop(process)
        self.assertEqual(app.after.call_count, 1)


if __name__ == "__main__":
    unittest.main()
