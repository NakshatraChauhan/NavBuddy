"""Configuration for BlindNav AI."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BlindNavConfig:
    """Runtime configuration values and feature approvals."""

    APP_NAME: str = "BlindNav AI"
    SECRET_KEY: str = "blindnav-dev-key"
    MODEL_PATH: Path = Path("models/yolov8n.pt")
    OSM_DATA_PATH: Path = Path("data/osm_map.json")
    LOG_PATH: Path = Path("blindnav.log")
    DETECTION_FPS: int = 5
    FOCAL_LENGTH_PX: float = 650.0
    CAMERA_APPROVED: bool = True
    GPS_APPROVED: bool = True
    MOTION_APPROVED: bool = False
    VIBRATION_APPROVED: bool = True
    SMS_APPROVED: bool = True


CONFIG = BlindNavConfig()
