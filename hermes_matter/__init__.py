"""Hermes Matter plugin.

Auto-discovers Matter devices on the LAN, lists their sensors and exposes
temperature/humidity behind a simple facade, with a provider architecture so
other ecosystems (Philips Hue, IKEA, Aqara, Eve, ...) can be added later
without touching the facade.
"""

from .hermes import Hermes
from .models import Device, Reading, Sensor, SensorType
from .providers.base import Provider, available_providers, register_provider

# Import built-in providers so they self-register.
from .providers import matter as _matter  # noqa: F401

__all__ = [
    "Hermes",
    "Device",
    "Reading",
    "Sensor",
    "SensorType",
    "Provider",
    "register_provider",
    "available_providers",
]

__version__ = "0.1.0"
