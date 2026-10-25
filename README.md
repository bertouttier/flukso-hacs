# Flukso integration for Home Assistant

This custom integration adds [Flukso](https://flukso.net/) energy monitors (FLM02 and FLM03), including their [Kube](https://www.flukso.net/files/presentations/flukso.20140424.pdf) sensors, to Home Assistant over the Flukso's local MQTT broker. No cloud connection is used.

## Requirements

- Home Assistant 2026.10 or newer.
- An MQTT broker with the [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) set up in Home Assistant.
- An MQTT bridge from your Flukso's broker to the broker Home Assistant uses (see [Bridging the Flukso broker](#bridging-the-flukso-broker)).

## Installation

1. In HACS, add `https://github.com/bertouttier/flukso-hacs` as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) of type **Integration**.
2. Install **Flukso** and restart Home Assistant.

To install manually, copy `custom_components/flukso` into the `custom_components` folder of your Home Assistant configuration and restart.

## Bridging the Flukso broker

Every Flukso runs its own MQTT broker on port 1883. Home Assistant needs to see its messages, so bridge the Flukso broker into the broker Home Assistant uses.

### Mosquitto broker add-on

1. In the configuration of the [Mosquitto broker add-on](https://github.com/home-assistant/addons/blob/master/mosquitto/DOCS.md), enable `customize` and set `folder` to `mosquitto`:

   ```yaml
   customize:
     active: true
     folder: mosquitto
   ```

2. Create `/share/mosquitto/flukso01.conf` (one file per Flukso, each with a unique `connection` name):

   ```ini
   connection flukso01
   address <flukso ip>:1883
   remote_clientid flukso01bridge
   cleansession true
   restart_timeout 5
   topic /device/# in 0
   topic /sensor/# in 0
   ```

3. Restart the add-on.

The add-on loads every `.conf` file in that folder as broker configuration. If you also use an ACL file, give it a name without the `.conf` extension (for example `/share/mosquitto/accesscontrollist`) and point to it from a `.conf` file with `acl_file /share/mosquitto/accesscontrollist`.

### Other brokers

Configure a bridge that imports the `/device/#` and `/sensor/#` topics from `<flukso ip>:1883`. See your broker's documentation for the syntax.

## Adding a Flukso

### Discovery

Once the bridge is up, Home Assistant discovers every Flukso that publishes its configuration. Go to **Settings > Devices & services**, confirm the discovered Flukso, and all its enabled sensors are added.

### Manually

You need the device hash of the Flukso (not a sensor hash). Connect an MQTT client such as [MQTT Explorer](http://mqtt-explorer.com) to Home Assistant's broker and look at the topics under `/device/`. They have the form `/device/<device hash>/config/<something>`; the 32 character `<device hash>` is what you need.

Then [add the Flukso integration](https://my.home-assistant.io/redirect/config_flow_start/?domain=flukso) and enter the device hash.

## What you get

Each Flukso becomes one device. An FLM03 is recognised by its TAP report and shows its serial number and firmware version; any other Flukso is shown as an FLM02.

Each sensor that is enabled on the Flukso becomes one or more entities. They are named after the Flukso port or Kube name you configured on the Flukso, followed by the sensor type, for example `L1 electricity pplus counter` or `keuken temperature`.

| Flukso sensor | Entities | Unit |
|---|---|---|
| Electricity (FLM02) | power, energy | W, Wh |
| Electricity pplus / pminus (FLM03) | power, energy | W, Wh |
| Electricity q1–q4 (FLM03) | reactive power, reactive energy | var, varh |
| Electricity vrms, irms, pf (FLM03) | voltage, current, power factor | V, A, % |
| Electricity vthd, ithd, alpha (FLM03) | one measurement each | – |
| Water | flow, total | L/s, L |
| Gas | flow, total | m³/s, m³ |
| Kube temperature, humidity, pressure, light | one measurement each | °C, %, hPa, lx |
| Kube proximity | one measurement | – |
| Kube battery (diagnostic) | battery level | % |
| Kube movement, vibration | binary sensor, on for 10 s after each event | – |
| Kube error (diagnostic) | binary sensor | – |

Energy, water and gas totals can be used in the Energy dashboard.

A state is only written when the value changes, and noisy Kube readings are rounded (temperature to 0.1 °C, the others to whole numbers), so sensors that rarely change do not fill the recorder database. Entities become unavailable while Home Assistant is disconnected from the MQTT broker.

When you change the sensor, flx or kube configuration on the Flukso (for example rename a Kube or enable a sensor), the integration reloads and picks up the change automatically.

## Upgrading from 1.x

Version 2.0 is a rewrite that no longer relies on internals of the MQTT integration.

- Entity IDs and history are kept.
- Entity names now include the sensor type, for example `keuken pressure` instead of `keuken`.
- Water and gas flow now use the volume flow rate device class, and reactive energy uses `varh`.
- Only battery and error sensors are diagnostic entities; the others are regular entities.
- Kube battery is reported in whole percents.
- The empty duplicate Flukso device that version 1.x left behind is removed automatically.

## Troubleshooting

**The Flukso shows "Retrying setup".** Home Assistant did not receive `/device/<device hash>/config/sensor` within 10 seconds. Check that the bridge is connected and that the topic is visible on Home Assistant's broker. Setup is retried automatically.

**Debug logging.** Add this to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.flukso: debug
```

## Development

The tests run against the Home Assistant version pinned in `requirements_test.txt`, using a simulated Flukso and MQTT broker (`tests/flukso_simulator.py`):

```bash
pip install -r requirements_test.txt
pytest
```
