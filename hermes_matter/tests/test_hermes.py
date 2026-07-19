"""Tests for the Hermes facade and Matter parsing.

These run without any hardware or a Matter server: the Matter server client is
replaced by a fake that returns a canned ``get_nodes`` payload.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hermes_matter import Hermes, SensorType
from hermes_matter.config import RoomConfig
from hermes_matter.providers.matter import MatterProvider, _parse_measurement


class FakeClient:
    def __init__(self, nodes):
        self._nodes = nodes

    async def get_nodes(self):
        return self._nodes


NODES = [
    {
        "node_id": 4,
        "attributes": {
            "0/40/5": "Living Room",
            "1/1026/0": 2150,  # 21.50 °C
            "1/1029/0": 4500,  # 45.00 %
        },
    },
    {
        "node_id": 7,
        "attributes": {
            "0/40/3": "Bedroom",
            "1/1026/0": 1900,  # 19.00 °C
        },
    },
]


def make_hermes(nodes=NODES):
    rooms = RoomConfig({"stue": ["4"], "soveværelse": ["7"]})
    provider = MatterProvider(rooms=rooms, client_factory=lambda: FakeClient(nodes))
    return Hermes(providers=[provider])


def test_parse_temperature():
    endpoint, stype, reading = _parse_measurement("1/1026/0", 2150)
    assert endpoint == 1
    assert stype is SensorType.TEMPERATURE
    assert reading.value == 21.5
    assert reading.unit == "°C"


def test_parse_humidity():
    _, stype, reading = _parse_measurement("2/1029/0", 5025)
    assert stype is SensorType.HUMIDITY
    assert reading.value == 50.25


def test_parse_ignores_unknown_clusters():
    assert _parse_measurement("1/6/0", 1) is None  # OnOff cluster
    assert _parse_measurement("1/1026/1", 5) is None  # not MeasuredValue
    assert _parse_measurement("bad-key", 5) is None


def test_list_sensors_builds_expected_sensors():
    hermes = make_hermes()
    sensors = hermes.list_sensors()
    ids = {s.id for s in sensors}
    assert "matter:4:1:temperature" in ids
    assert "matter:4:1:humidity" in ids
    assert "matter:7:1:temperature" in ids
    assert len(sensors) == 3


def test_room_assignment():
    hermes = make_hermes()
    stue = hermes.list_sensors("stue")
    assert {s.type for s in stue} == {SensorType.TEMPERATURE, SensorType.HUMIDITY}
    assert all(s.room == "stue" for s in stue)


def test_get_temperature_and_humidity():
    hermes = make_hermes()
    assert hermes.get_temperature("stue") == 21.5
    assert hermes.get_humidity("stue") == 45.0
    assert hermes.get_temperature("soveværelse") == 19.0
    assert hermes.get_humidity("soveværelse") is None  # no humidity sensor


def test_get_temperature_averages_multiple_sensors():
    nodes = [
        {
            "node_id": 4,
            "attributes": {"0/40/5": "Living Room A", "1/1026/0": 2000},
        },
        {
            "node_id": 44,
            "attributes": {"0/40/5": "Living Room B", "1/1026/0": 2200},
        },
    ]
    rooms = RoomConfig({"stue": ["4", "44"]})
    provider = MatterProvider(rooms=rooms, client_factory=lambda: FakeClient(nodes))
    hermes = Hermes(providers=[provider])
    assert hermes.get_temperature("stue") == 21.0  # mean of 20.0 and 22.0


def test_unknown_room_returns_none():
    hermes = make_hermes()
    assert hermes.get_temperature("badeværelse") is None


def test_device_centric_access():
    nodes = [
        {
            "node_id": 4,
            "attributes": {
                "0/40/5": "SwitchBot Hub 2",
                "1/1026/0": 2150,
                "1/1029/0": 4500,
            },
        }
    ]
    rooms = RoomConfig({"stue": ["4"]})
    provider = MatterProvider(rooms=rooms, client_factory=lambda: FakeClient(nodes))
    hermes = Hermes(providers=[provider])

    devices = hermes.devices
    assert "SwitchBot Hub 2" in devices
    hub = devices["SwitchBot Hub 2"]
    assert hub.temperature == 21.5
    assert hub.humidity == 45.0
    assert hub.room == "stue"
    assert len(hub.sensors) == 2


def test_cache_avoids_repeated_reads():
    calls = {"n": 0}

    class CountingClient:
        async def get_nodes(self):
            calls["n"] += 1
            return NODES

    provider = MatterProvider(client_factory=lambda: CountingClient())
    hermes = Hermes(providers=[provider], cache_ttl=60)

    hermes.list_sensors()
    hermes.get_temperature("stue")
    _ = hermes.devices
    assert calls["n"] == 1  # served from cache after the first read

    hermes.refresh()
    assert calls["n"] == 2  # explicit refresh bypasses the cache


def test_cache_ttl_zero_always_refreshes():
    calls = {"n": 0}

    class CountingClient:
        async def get_nodes(self):
            calls["n"] += 1
            return NODES

    provider = MatterProvider(client_factory=lambda: CountingClient())
    hermes = Hermes(providers=[provider], cache_ttl=0)

    hermes.list_sensors()
    hermes.list_sensors()
    assert calls["n"] == 2


def test_server_unreachable_degrades_gracefully():
    class BrokenClient:
        async def get_nodes(self):
            raise ConnectionError("server down")

    provider = MatterProvider(client_factory=lambda: BrokenClient())
    hermes = Hermes(providers=[provider])
    assert hermes.list_sensors() == []
    assert hermes.get_temperature("stue") is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
