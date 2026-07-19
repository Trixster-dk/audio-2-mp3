"""The Hermes facade.

This is the surface the rest of Hermes (the agent) talks to. It hides async
plumbing and the provider registry behind a plain, synchronous API::

    hermes = Hermes(config_path="hermes_matter/rooms.example.json")
    hermes.get_temperature("stue")   # -> 21.5
    hermes.get_humidity("stue")      # -> 45.0

Providers are aggregated: whichever integrations are registered (Matter today;
Hue/IKEA/Aqara/Eve later) all contribute sensors to the same room lookup.
"""

from __future__ import annotations

import asyncio
import logging
import time
from statistics import mean
from typing import Dict, List, Optional

from .config import RoomConfig
from .models import Device, HermesDevice, Sensor, SensorType
from .providers.base import Provider, available_providers

logger = logging.getLogger(__name__)


class Hermes:
    def __init__(
        self,
        config_path: Optional[str] = None,
        providers: Optional[List[Provider]] = None,
        cache_ttl: float = 30.0,
    ):
        self.rooms = RoomConfig.load(config_path)
        if providers is not None:
            self._providers = providers
        else:
            self._providers = [
                cls(rooms=self.rooms) if _accepts_rooms(cls) else cls()
                for cls in available_providers().values()
            ]
        self._cache_ttl = cache_ttl
        self._cache: Optional[List[Sensor]] = None
        self._cache_time = 0.0

    # -- public, synchronous API ------------------------------------------

    def discover(self) -> List[Device]:
        """Return every device visible across all providers."""

        return _run(self._gather(lambda p: p.discover()))

    def refresh(self) -> "Hermes":
        """Force a fresh read of all sensors into the cache."""

        self._read_sensors(force=True)
        return self

    def list_sensors(self, room: Optional[str] = None) -> List[Sensor]:
        """Return all sensors, optionally filtered to one room."""

        sensors = self._read_sensors()
        if room is not None:
            sensors = [s for s in sensors if s.room == room]
        return sensors

    @property
    def devices(self) -> Dict[str, HermesDevice]:
        """Return a name-keyed registry of devices with their sensors.

        Enables ``hermes.devices["SwitchBot Hub 2"].temperature``. Values come
        from the same cache as the room API, so both views stay consistent.
        """

        registry: Dict[str, HermesDevice] = {}
        for sensor in self._read_sensors():
            name = sensor.device_name or sensor.device_id
            device = registry.get(name)
            if device is None:
                device = HermesDevice(
                    id=sensor.device_id,
                    name=name,
                    provider=sensor.provider,
                    room=sensor.room,
                )
                registry[name] = device
            device.sensors.append(sensor)
        return registry

    def get_temperature(self, room: str) -> Optional[float]:
        """Return the temperature in ``room`` in °C (averaged if several)."""

        return self._aggregate(room, SensorType.TEMPERATURE)

    def get_humidity(self, room: str) -> Optional[float]:
        """Return the relative humidity in ``room`` in % (averaged if several)."""

        return self._aggregate(room, SensorType.HUMIDITY)

    # -- internals ---------------------------------------------------------

    def _read_sensors(self, force: bool = False) -> List[Sensor]:
        """Return sensors from cache, refreshing when stale or forced."""

        now = time.monotonic()
        fresh = self._cache is not None and (now - self._cache_time) < self._cache_ttl
        if force or not fresh:
            self._cache = _run(self._gather(lambda p: p.list_sensors()))
            self._cache_time = now
        return self._cache

    def _aggregate(self, room: str, sensor_type: SensorType) -> Optional[float]:
        values = [
            s.reading.value
            for s in self.list_sensors(room)
            if s.type == sensor_type and s.reading is not None
        ]
        if not values:
            logger.info("No %s sensor with a reading in room %r", sensor_type.value, room)
            return None
        return round(mean(values), 2)

    async def _gather(self, action):
        results: list = []
        for provider in self._providers:
            try:
                results.extend(await action(provider))
            except Exception as exc:  # noqa: BLE001 - one provider must not sink the rest
                logger.warning("Provider %s failed: %s", provider.name, exc)
        return results


def _accepts_rooms(cls) -> bool:
    import inspect

    try:
        return "rooms" in inspect.signature(cls).parameters
    except (ValueError, TypeError):
        return False


def _run(coro):
    """Run an async coroutine from sync code, even if a loop already exists."""

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # Already inside an event loop: run in a dedicated thread.
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(coro)).result()
