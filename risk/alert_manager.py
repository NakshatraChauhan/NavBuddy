"""Manage anti-spam alert decisions for voice/haptic cues."""
from __future__ import annotations

import time
from typing import Dict


class AlertManager:
    """Rate-limit repeated alerts per object and risk message."""

    def __init__(self, cooldown_s: float = 3.0) -> None:
        self.cooldown_s = cooldown_s
        self.last_alerts: Dict[str, float] = {}

    def should_alert(self, key: str) -> bool:
        now = time.time()
        last = self.last_alerts.get(key, 0)
        if now - last >= self.cooldown_s:
            self.last_alerts[key] = now
            return True
        return False
