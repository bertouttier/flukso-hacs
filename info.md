## Flukso

Adds [Flukso](https://flukso.net/) energy monitors (FLM02 and FLM03) and their Kube sensors to Home Assistant over the Flukso's local MQTT broker.

- Power, energy, reactive power and energy, voltage, current and power factor
- Water and gas flow and totals, ready for the Energy dashboard
- Kube temperature, humidity, pressure, light, battery, movement, vibration and errors
- Discovered automatically once the Flukso broker is bridged to Home Assistant's broker

Requires Home Assistant 2026.10 or newer, the MQTT integration, and an MQTT bridge from the Flukso to Home Assistant's broker. See the [documentation](https://github.com/bertouttier/flukso-hacs#readme) for setup instructions.
