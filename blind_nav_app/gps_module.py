from typing import Dict

import requests


def describe_location(lat: float, lon: float) -> Dict:
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "jsonv2"},
            headers={"User-Agent": "blind-nav-assistant/1.0"},
            timeout=3,
        )
        response.raise_for_status()
        payload = response.json()
        display_name = payload.get("display_name", "your current area")
        short = display_name.split(",")[:2]
        spoken = ", ".join(short)
        return {"ok": True, "location": spoken, "raw": display_name}
    except Exception:
        return {"ok": False, "location": "your current area", "raw": ""}
