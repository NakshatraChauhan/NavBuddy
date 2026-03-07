from __future__ import annotations

import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# Lightweight stubs so tests can run in minimal environments.
if "numpy" not in sys.modules:
    np_stub = types.ModuleType("numpy")
    np_stub.ndarray = object
    sys.modules["numpy"] = np_stub

if "cv2" not in sys.modules:
    cv2_stub = types.ModuleType("cv2")
    cv2_stub.CAP_PROP_FRAME_WIDTH = 3
    cv2_stub.CAP_PROP_FRAME_HEIGHT = 4
    cv2_stub.CAP_PROP_FPS = 5
    cv2_stub.INTER_AREA = 1
    cv2_stub.resize = lambda frame, size, interpolation=None: frame
    cv2_stub.VideoCapture = object
    sys.modules["cv2"] = cv2_stub

if "ultralytics" not in sys.modules:
    u_stub = types.ModuleType("ultralytics")

    class YOLO:  # noqa: N801
        def __init__(self, *args, **kwargs):
            pass

        def predict(self, *args, **kwargs):
            return []

    u_stub.YOLO = YOLO
    sys.modules["ultralytics"] = u_stub


if "speech_recognition" not in sys.modules:
    sr_stub = types.ModuleType("speech_recognition")

    class Recognizer:
        def adjust_for_ambient_noise(self, *args, **kwargs):
            return None

    class Microphone:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class WaitTimeoutError(Exception):
        pass

    class UnknownValueError(Exception):
        pass

    class RequestError(Exception):
        pass

    sr_stub.Recognizer = Recognizer
    sr_stub.Microphone = Microphone
    sr_stub.WaitTimeoutError = WaitTimeoutError
    sr_stub.UnknownValueError = UnknownValueError
    sr_stub.RequestError = RequestError
    sys.modules["speech_recognition"] = sr_stub
from ai.detector import Detection, ObstacleDetector
from ai.scene_analyzer import SceneAnalyzer
from navigation.navigator import Navigator
from permissions.permission_manager import PermissionManager
from voice.voice_controller import VoiceController


class TestPermissionManager(unittest.TestCase):
    def test_env_permissions_are_applied(self):
        logger = MagicMock()
        pm = PermissionManager(logger)
        with patch("os.getenv") as getenv:
            mapping = {
                "BLINDNAV_PERMISSION_CAMERA": "yes",
                "BLINDNAV_PERMISSION_MICROPHONE": "no",
                "BLINDNAV_PERMISSION_GPS": "true",
                "BLINDNAV_PERMISSION_SPEAKER": "1",
                "BLINDNAV_AUTO_APPROVE": "false",
            }
            getenv.side_effect = lambda key, default=None: mapping.get(key, default)
            state = pm.request_all()
        self.assertTrue(state.camera)
        self.assertFalse(state.microphone)
        self.assertTrue(state.gps)
        self.assertTrue(state.speaker)


class TestDetector(unittest.TestCase):
    @patch("ai.detector.YOLO")
    def test_model_loading(self, yolo_cls):
        logger = MagicMock()
        detector = ObstacleDetector("models/yolov8n.pt", logger=logger)
        self.assertIsNotNone(detector.model)
        yolo_cls.assert_called_once()


class TestVoiceAndNavigation(unittest.TestCase):
    def _build_nav(self):
        permissions = SimpleNamespace(camera=True, microphone=True, gps=False, speaker=True)
        detector = MagicMock()
        detector.last_inference_ms = 0.0
        detector.detect.return_value = [Detection("person", 0.9, [100, 0, 200, 100])]
        analyzer = SceneAnalyzer(logger=MagicMock())
        speech = MagicMock()
        navigator = Navigator(detector, analyzer, speech, logger=MagicMock(), permissions=permissions, target_fps=4)
        return navigator, speech

    def test_help_command_response(self):
        navigator, _ = self._build_nav()
        voice = VoiceController(navigator, MagicMock(), logger=MagicMock(), permissions=SimpleNamespace(microphone=True))
        response = voice.handle_command("help")
        self.assertIn("Available commands are:", response)
        self.assertIn("start navigation", response)

    def test_navigation_alert_generation(self):
        navigator, speech = self._build_nav()

        class Frame:
            shape = (480, 640, 3)

        frame = Frame()
        with patch("navigation.navigator.cv2.VideoCapture") as cap_cls:
            cap = MagicMock()
            cap.isOpened.return_value = True
            cap.read.return_value = (True, frame)
            cap_cls.return_value = cap

            message = navigator.describe_scene_once()

        self.assertTrue(message)
        speech.speak.assert_called()


if __name__ == "__main__":
    unittest.main()
