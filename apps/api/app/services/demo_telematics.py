"""Demo telematics helpers — deterministic positions for pilot UI without live Wialon."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from uuid import UUID

# Moscow → SPb corridor approximate anchors
_MOSCOW = (55.7558, 37.6173)
_SPB = (59.9343, 30.3351)


def demo_position_for_index(index: int, *, moving: bool = True) -> dict:
    """Spread vehicles along Moscow–SPb corridor with slight offsets."""
    t = (index % 20) / 19.0
    lat = _MOSCOW[0] + (_SPB[0] - _MOSCOW[0]) * t + math.sin(index) * 0.08
    lon = _MOSCOW[1] + (_SPB[1] - _MOSCOW[1]) * t + math.cos(index) * 0.12
    speed = 62.0 + (index % 7) * 3.5 if moving else 0.0
    return {
        "lat": round(lat, 5),
        "lon": round(lon, 5),
        "speed_kmh": round(speed, 1),
        "heading": (index * 17) % 360,
        "ignition": moving,
        "updated_at": datetime.now(UTC).isoformat(),
        "source": "wialon_demo",
    }


def motion_status(position: dict | None, vehicle_status: str) -> str:
    if vehicle_status == "inactive":
        return "offline"
    if vehicle_status == "maintenance":
        return "offline"
    if not position:
        return "offline"
    speed = float(position.get("speed_kmh") or 0)
    if speed >= 5:
        return "moving"
    if position.get("ignition"):
        return "idle"
    return "parked"


ROUTE_PAIRS = [
    ("Москва", "Санкт-Петербург"),
    ("Казань", "Нижний Новгород"),
    ("Екатеринбург", "Челябинск"),
    ("Самара", "Уфа"),
    ("Тверь", "Москва"),
    ("Вологда", "Ярославль"),
]


def demo_order_details(index: int, vehicle_id: UUID | None = None) -> dict:
    origin, destination = ROUTE_PAIRS[index % len(ROUTE_PAIRS)]
    return {
        "origin": {"name": origin},
        "destination": {"name": destination},
        "cargo": {
            "description": "Генеральный груз" if index % 3 else "Негабарит (пилот)",
            "mass_kg": 12000 + index * 800,
            "length_m": 12 + (index % 5) * 0.6,
            "width_m": 2.4 + (index % 3) * 0.2,
            "height_m": 3.2 + (index % 4) * 0.15,
        },
        "vehicle_id": str(vehicle_id) if vehicle_id else None,
        "source": "transmanager_demo",
        "notes": "Импорт из ТрансМенеджер (DEMO)",
    }
