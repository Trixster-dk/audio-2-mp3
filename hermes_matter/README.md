# Hermes Matter plugin

A plugin that lets **Hermes** talk to smart-home sensors. It:

- automatically finds **Matter** devices on the LAN (mDNS / DNS-SD)
- lists all sensors
- reads **temperature** and **humidity**
- exposes them behind a simple facade:

```python
from hermes_matter import Hermes

hermes = Hermes(config_path="hermes_matter/rooms.example.json")

hermes.get_temperature("stue")   # -> 21.5   (°C)
hermes.get_humidity("stue")      # -> 45.0   (%)
```

Later you can add **Philips Hue, IKEA, Aqara, Eve** etc. by writing one
`Provider` subclass each — the `Hermes` facade and the room lookup stay
exactly the same.

## Architecture

```
Hermes (facade, sync API)
  └── Provider registry
        ├── MatterProvider          (built in)
        ├── HueProvider    ← add later
        ├── IkeaProvider   ← add later
        └── ...
```

- `models.py` — provider-agnostic `Device`, `Sensor`, `Reading` types.
- `providers/base.py` — the `Provider` interface + `@register_provider`.
- `providers/matter.py` — Matter integration.
- `discovery.py` — mDNS discovery of Matter devices.
- `config.py` — maps devices to room names.
- `hermes.py` — the synchronous facade that aggregates all providers.
- `cli.py` — `python -m hermes_matter …`.

### How the two halves fit together

Matter data can't be read straight off the wire — a device only hands out its
values to a **controller** that shares a fabric with it. So the plugin splits
the job:

1. **Discovery** (`discovery.py`) listens to mDNS and tells you *which* Matter
   devices exist on the LAN. This needs no controller, no pairing — it works
   on its own.
2. **Reading values** goes through a running
   [`python-matter-server`](https://github.com/home-assistant-libs/python-matter-server)
   (the same server Home Assistant uses) over its websocket API. Hermes speaks
   that API directly, so it never has to embed the heavy Matter SDK itself.

If the server isn't reachable, discovery still works and reads degrade
gracefully to "no value" with a logged warning.

## Adding a new provider (e.g. Philips Hue)

```python
from hermes_matter.providers.base import Provider, register_provider
from hermes_matter.models import Sensor, SensorType, Reading

@register_provider
class HueProvider(Provider):
    name = "hue"

    async def discover(self):
        ...   # find the Hue bridge

    async def list_sensors(self):
        ...   # return Sensor(...) objects, tagged with room + reading
```

Import it once (e.g. in `hermes_matter/__init__.py`) and it auto-registers.
`hermes.get_temperature("stue")` will then transparently include Hue sensors.

## Setup

```bash
pip install -r hermes_matter/requirements.txt
```

For live values, run a Matter server (see the python-matter-server docs) and
point Hermes at it if it isn't on the default `ws://localhost:5580/ws`:

```bash
export HERMES_MATTER_SERVER_URL="ws://<host>:5580/ws"
```

## CLI

```bash
python -m hermes_matter scan                 # discover devices on the LAN
python -m hermes_matter sensors              # list all sensors + readings
python -m hermes_matter sensors stue         # only the living room
python -m hermes_matter temp stue            # temperature in a room
python -m hermes_matter humidity stue        # humidity in a room
python -m hermes_matter --config hermes_matter/rooms.example.json sensors
```

## Room configuration

`rooms.example.json` maps devices to rooms. A key matches a device when it
equals the device's node id **or** is a substring of its name:

```json
{
  "rooms": {
    "stue": ["4", "Living Room"],
    "soveværelse": ["7"]
  }
}
```

## Tests

Run without any hardware — the Matter server client is faked:

```bash
python -m pytest hermes_matter/tests/ -q
```
