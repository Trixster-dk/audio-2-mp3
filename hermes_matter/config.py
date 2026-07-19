"""Room mapping configuration.

Sensors report a device id and a name; a human wants to ask for "stue"
(living room). This maps device identifiers to room names so
``hermes.get_temperature("stue")`` works.

The config is a small JSON file, for example::

    {
      "rooms": {
        "stue": ["4", "Living Room Sensor"],
        "soveværelse": ["7"]
      }
    }

Each room lists device keys that belong to it. A key matches a device when it
equals the device's node id, or is a case-insensitive substring of the device
name.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Union


class RoomConfig:
    def __init__(self, mapping: Dict[str, List[str]]):
        # Normalise to {room: [keys]} with string keys.
        self._rooms = {
            room: [str(k) for k in keys] for room, keys in mapping.items()
        }

    def room_for(self, device_id: str, device_name: str = "") -> Optional[str]:
        """Return the room a device belongs to, or ``None`` if unmapped."""

        device_id = str(device_id)
        name_lower = (device_name or "").lower()
        for room, keys in self._rooms.items():
            for key in keys:
                if key == device_id or (key and key.lower() in name_lower):
                    return room
        return None

    @property
    def rooms(self) -> List[str]:
        return list(self._rooms)

    @classmethod
    def load(cls, path: Union[str, Path, None]) -> "RoomConfig":
        """Load config from ``path``; return an empty config if it is missing."""

        if not path:
            return cls({})
        p = Path(path)
        if not p.exists():
            return cls({})
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(data.get("rooms", {}))
