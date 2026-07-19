"""Core data models shared by all Hermes providers.

These types are provider-agnostic on purpose: a Matter sensor, a Philips Hue
sensor and an Aqara sensor all get normalised into the same ``Sensor`` /
``Reading`` shapes so the ``Hermes`` facade never has to care where a value
came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SensorType(str, Enum):
    """Kind of measurement a sensor reports."""

    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    UNKNOWN = "unknown"


@dataclass
class Device:
    """A physical device discovered on the network.

    ``address``/``port`` come from mDNS discovery and are enough to tell that a
    device exists on the LAN, even before it can be read through a controller.
    """

    id: str
    name: str
    provider: str
    address: Optional[str] = None
    port: Optional[int] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Reading:
    """A single measurement taken from a sensor at a point in time."""

    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Sensor:
    """A logical sensor exposed by a device.

    A single device can expose several sensors (for example a combined
    temperature + humidity sensor shows up as two ``Sensor`` objects).
    """

    id: str
    name: str
    type: SensorType
    provider: str
    device_id: str
    room: Optional[str] = None
    reading: Optional[Reading] = None
