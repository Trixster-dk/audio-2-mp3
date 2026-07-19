"""Command line interface: ``python -m hermes_matter <command>``.

Commands
--------
scan                 Browse the LAN and list discovered Matter devices.
sensors [room]       List sensors (optionally filtered to a room) with values.
temp <room>          Print the temperature in a room.
humidity <room>      Print the humidity in a room.

Use ``--config PATH`` to point at a rooms JSON file.
"""

from __future__ import annotations

import argparse
import logging
import sys

from .hermes import Hermes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="hermes_matter", description=__doc__)
    parser.add_argument("--config", help="path to a rooms JSON config")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scan", help="discover devices on the LAN")

    p_sensors = sub.add_parser("sensors", help="list sensors and readings")
    p_sensors.add_argument("room", nargs="?", help="filter to this room")

    sub.add_parser("devices", help="list devices with their readings")

    p_temp = sub.add_parser("temp", help="temperature in a room")
    p_temp.add_argument("room")

    p_hum = sub.add_parser("humidity", help="humidity in a room")
    p_hum.add_argument("room")

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    hermes = Hermes(config_path=args.config)

    if args.command == "scan":
        return _scan(hermes)
    if args.command == "sensors":
        return _sensors(hermes, args.room)
    if args.command == "devices":
        return _devices(hermes)
    if args.command == "temp":
        return _reading(hermes.get_temperature(args.room), args.room, "°C")
    if args.command == "humidity":
        return _reading(hermes.get_humidity(args.room), args.room, "%")
    return 1


def _scan(hermes: Hermes) -> int:
    devices = hermes.discover()
    if not devices:
        print("No Matter devices found on the LAN.")
        return 0
    print(f"Found {len(devices)} device(s):")
    for d in devices:
        kind = "commissionable" if d.metadata.get("commissionable") else "operational"
        where = f"{d.address}:{d.port}" if d.address else "address unknown"
        print(f"  - {d.name} [{kind}] {where}")
    return 0


def _sensors(hermes: Hermes, room) -> int:
    sensors = hermes.list_sensors(room)
    if not sensors:
        print("No sensors available. Is the Matter server running?")
        return 0
    for s in sensors:
        value = f"{s.reading.value}{s.reading.unit}" if s.reading else "n/a"
        print(f"  - [{s.room or 'unassigned'}] {s.name}: {value}")
    return 0


def _devices(hermes: Hermes) -> int:
    devices = hermes.devices
    if not devices:
        print("No devices with readings. Is the Matter server running?")
        return 0
    for name, d in devices.items():
        temp = f"{d.temperature}°C" if d.temperature is not None else "n/a"
        hum = f"{d.humidity}%" if d.humidity is not None else "n/a"
        print(f"  - {name} [{d.room or 'unassigned'}]: temp={temp} humidity={hum}")
    return 0


def _reading(value, room, unit) -> int:
    if value is None:
        print(f"No reading available for room {room!r}.")
        return 1
    print(f"{value}{unit}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
