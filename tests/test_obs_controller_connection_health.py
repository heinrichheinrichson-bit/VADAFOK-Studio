import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.core.obs_controller import OBSController


class OBSControllerConnectionHealthTests(unittest.TestCase):
    def test_failed_handshake_cleans_up_partial_client(self):
        partial = Mock()
        partial.get_version.side_effect = RuntimeError("handshake failed")
        controller = OBSController()

        with patch("vadafok_studio.core.obs_controller.obs") as library:
            library.ReqClient.return_value = partial
            with self.assertRaises(RuntimeError):
                controller.connect("localhost", "4455", "")

        self.assertIsNone(controller.client)
        self.assertFalse(controller.connected)
        partial.disconnect.assert_called()

    def test_version_summary_uses_available_obs_fields(self):
        controller = OBSController()
        controller.last_version = SimpleNamespace(
            obs_version="32.0.0", obs_web_socket_version="5.6.0",
        )

        self.assertEqual(
            controller.version_summary(), "OBS 32.0.0 · WebSocket 5.6.0",
        )

    def test_failed_probe_hard_disconnects_stale_client(self):
        controller = OBSController()
        stale = Mock()
        stale.get_version.side_effect = RuntimeError("socket closed")
        controller.client = stale
        controller.connected = True

        self.assertFalse(controller.probe())

        self.assertIsNone(controller.client)
        stale.disconnect.assert_called()


if __name__ == "__main__":
    unittest.main()
