"""mDNS / DNS-SD discovery of Matter devices on the local network.

Matter devices advertise themselves over mDNS:

* ``_matterc._udp`` -- commissionable (not yet paired) devices
* ``_matter._tcp``  -- operational (paired) devices on a fabric

This module needs no controller, no fabric and no commissioning credentials --
it just listens to what devices already announce on the LAN. That makes it a
reliable "is anything out there?" probe even when a Matter controller is not
running.
"""

from __future__ import annotations

import asyncio
from typing import List

from .models import Device

MATTER_COMMISSIONABLE = "_matterc._udp.local."
MATTER_OPERATIONAL = "_matter._tcp.local."


def _require_zeroconf():
    try:
        import zeroconf  # noqa: F401
        from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf  # noqa: F401
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ImportError(
            "mDNS discovery requires the 'zeroconf' package. "
            "Install it with: pip install -r hermes_matter/requirements.txt"
        ) from exc


async def discover_matter_devices(timeout: float = 4.0) -> List[Device]:
    """Browse the LAN for Matter devices for ``timeout`` seconds.

    Returns one :class:`Device` per advertised service instance. Duplicate
    instances (same name across both service types) are collapsed by id.
    """

    _require_zeroconf()
    from zeroconf import ServiceStateChange
    from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

    found: dict[str, Device] = {}
    aiozc = AsyncZeroconf()

    def on_change(zeroconf, service_type, name, state_change):
        if state_change is not ServiceStateChange.Added:
            return
        asyncio.ensure_future(_resolve(aiozc, service_type, name, found))

    browser = AsyncServiceBrowser(
        aiozc.zeroconf,
        [MATTER_COMMISSIONABLE, MATTER_OPERATIONAL],
        handlers=[on_change],
    )
    try:
        await asyncio.sleep(timeout)
    finally:
        await browser.async_cancel()
        await aiozc.async_close()

    return list(found.values())


async def _resolve(aiozc, service_type: str, name: str, found: dict) -> None:
    from zeroconf.asyncio import AsyncServiceInfo

    info = AsyncServiceInfo(service_type, name)
    if not await info.async_request(aiozc.zeroconf, 3000):
        return

    addresses = info.parsed_addresses() if hasattr(info, "parsed_addresses") else []
    address = addresses[0] if addresses else None
    properties = {
        _decode(k): _decode(v)
        for k, v in (info.properties or {}).items()
    }

    device_id = name.split(".")[0]
    found[device_id] = Device(
        id=device_id,
        name=properties.get("DN") or device_id,
        provider="matter",
        address=address,
        port=info.port,
        metadata={
            "service_type": service_type,
            "commissionable": service_type == MATTER_COMMISSIONABLE,
            **properties,
        },
    )


def _decode(value):
    if isinstance(value, bytes):
        try:
            return value.decode()
        except UnicodeDecodeError:
            return value.hex()
    return value
