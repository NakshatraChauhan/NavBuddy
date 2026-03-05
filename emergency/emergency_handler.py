"""Emergency mode orchestration."""
from __future__ import annotations

from typing import Dict

from utils.helpers import now_iso


class EmergencyHandler:
    """Handle emergency activation and optional SMS dispatch."""

    def __init__(self, sms_approved: bool = False) -> None:
        self.sms_approved = sms_approved

    def trigger(self, lat: float, lon: float, phone_number: str | None = None) -> Dict:
        response = {
            "status": "activated",
            "message": "Emergency mode activated",
            "timestamp": now_iso(),
            "location": {"lat": lat, "lon": lon},
            "sms_sent": False,
        }
        if self.sms_approved and phone_number:
            # In production, integrate gateway such as Twilio here.
            response["sms_sent"] = True
            response["sms_to"] = phone_number
        return response
