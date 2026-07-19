"""Provider abstraction and registry.

A *provider* is an integration for one ecosystem (Matter, Philips Hue, IKEA,
Aqara, Eve, ...). Adding support for a new ecosystem means writing one
``Provider`` subclass and decorating it with :func:`register_provider` -- no
changes to the ``Hermes`` facade are needed. That is the whole point of the
architecture: new brands plug in, they don't get hard-coded.
"""

from __future__ import annotations

import abc
from typing import Dict, List, Optional, Type

from ..models import Device, Reading, Sensor


class Provider(abc.ABC):
    """Base class every ecosystem integration implements."""

    #: Stable, unique provider name (used in sensor ids and the registry).
    name: str = "provider"

    @abc.abstractmethod
    async def discover(self) -> List[Device]:
        """Return the devices this provider can currently see on the network."""

    @abc.abstractmethod
    async def list_sensors(self) -> List[Sensor]:
        """Return the sensors this provider exposes, with a snapshot reading."""

    async def read(self, sensor: Sensor) -> Optional[Reading]:
        """Return a fresh reading for ``sensor``.

        The default implementation re-lists sensors and returns the matching
        snapshot, which is enough for providers whose ``list_sensors`` already
        fetches live values. Providers can override for a cheaper direct read.
        """

        for candidate in await self.list_sensors():
            if candidate.id == sensor.id:
                return candidate.reading
        return None

    async def close(self) -> None:
        """Release any resources (connections, browsers). Optional."""


_PROVIDERS: Dict[str, Type[Provider]] = {}


def register_provider(cls: Type[Provider]) -> Type[Provider]:
    """Class decorator that registers a provider under its ``name``."""

    if not getattr(cls, "name", None) or cls.name == "provider":
        raise ValueError(f"{cls.__name__} must define a unique 'name'")
    _PROVIDERS[cls.name] = cls
    return cls


def available_providers() -> Dict[str, Type[Provider]]:
    """Return a copy of the provider registry keyed by name."""

    return dict(_PROVIDERS)
