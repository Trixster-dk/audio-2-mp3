"""Matter provider.

Discovery is done directly over mDNS (see :mod:`hermes_matter.discovery`) and
needs nothing else. Reading sensor *values*, however, requires a Matter
controller that holds the fabric and can talk to the devices -- Matter data is
not readable straight off the wire. We use the well-established
``python-matter-server`` websocket API for that (the same server Home Assistant
uses), so Hermes never has to embed the heavy Matter SDK itself.

If the server is not reachable, discovery still works and ``list_sensors``
degrades gracefully to an empty list with a logged warning.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Callable, List, Optional

from ..config import RoomConfig
from ..models import Device, Reading, Sensor, SensorType
from .base import Provider, register_provider

logger = logging.getLogger(__name__)

# Matter cluster / attribute ids for the measurements we care about.
CLUSTER_BASIC_INFORMATION = 40  # 0x0028
ATTR_PRODUCT_NAME = 3
ATTR_NODE_LABEL = 5

CLUSTER_TEMPERATURE = 1026  # 0x0402 TemperatureMeasurement
CLUSTER_HUMIDITY = 1029  # 0x0405 RelativeHumidityMeasurement
ATTR_MEASURED_VALUE = 0

DEFAULT_SERVER_URL = os.environ.get(
    "HERMES_MATTER_SERVER_URL", "ws://localhost:5580/ws"
)


class MatterServerError(RuntimeError):
    """Raised when the Matter server returns an error response."""


class MatterServerClient:
    """Minimal async client for the python-matter-server websocket API."""

    def __init__(self, url: str = DEFAULT_SERVER_URL, timeout: float = 10.0):
        self.url = url
        self.timeout = timeout

    async def get_nodes(self) -> List[dict]:
        """Return all commissioned nodes with their attribute snapshots."""

        import websockets  # imported lazily so discovery works without it

        async with websockets.connect(self.url, open_timeout=self.timeout) as ws:
            await ws.recv()  # ServerInfoMessage handshake
            await ws.send(json.dumps({"message_id": "1", "command": "get_nodes"}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("message_id") != "1":
                    continue
                if "result" in msg:
                    return msg["result"]
                raise MatterServerError(msg.get("error_code", "unknown error"))


@register_provider
class MatterProvider(Provider):
    """Discovers Matter devices and reads their temperature/humidity sensors."""

    name = "matter"

    def __init__(
        self,
        server_url: str = DEFAULT_SERVER_URL,
        rooms: Optional[RoomConfig] = None,
        client_factory: Optional[Callable[[], MatterServerClient]] = None,
    ):
        self.server_url = server_url
        self.rooms = rooms or RoomConfig({})
        self._client_factory = client_factory or (
            lambda: MatterServerClient(server_url)
        )

    async def discover(self) -> List[Device]:
        from ..discovery import discover_matter_devices

        return await discover_matter_devices()

    async def list_sensors(self) -> List[Sensor]:
        try:
            nodes = await self._client_factory().get_nodes()
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            logger.warning(
                "Could not reach Matter server at %s (%s). "
                "Sensor values are unavailable; discovery still works.",
                self.server_url,
                exc,
            )
            return []

        sensors: List[Sensor] = []
        for node in nodes:
            sensors.extend(self._sensors_for_node(node))
        return sensors

    def _sensors_for_node(self, node: dict) -> List[Sensor]:
        node_id = str(node.get("node_id"))
        attrs = node.get("attributes", {}) or {}
        label = (
            attrs.get(f"0/{CLUSTER_BASIC_INFORMATION}/{ATTR_NODE_LABEL}")
            or attrs.get(f"0/{CLUSTER_BASIC_INFORMATION}/{ATTR_PRODUCT_NAME}")
            or f"Matter node {node_id}"
        )
        room = self.rooms.room_for(node_id, label)

        sensors: List[Sensor] = []
        for key, raw in attrs.items():
            parsed = _parse_measurement(key, raw)
            if parsed is None:
                continue
            endpoint, sensor_type, reading = parsed
            sensors.append(
                Sensor(
                    id=f"matter:{node_id}:{endpoint}:{sensor_type.value}",
                    name=f"{label} ({sensor_type.value})",
                    type=sensor_type,
                    provider=self.name,
                    device_id=node_id,
                    room=room,
                    reading=reading,
                )
            )
        return sensors


def _parse_measurement(key: str, raw) -> Optional[tuple]:
    """Turn an ``"endpoint/cluster/attribute"`` entry into a sensor reading."""

    try:
        endpoint, cluster, attribute = (int(part) for part in key.split("/"))
    except (ValueError, AttributeError):
        return None
    if attribute != ATTR_MEASURED_VALUE or raw is None:
        return None

    if cluster == CLUSTER_TEMPERATURE:
        return endpoint, SensorType.TEMPERATURE, Reading(raw / 100.0, "°C")
    if cluster == CLUSTER_HUMIDITY:
        return endpoint, SensorType.HUMIDITY, Reading(raw / 100.0, "%")
    return None
