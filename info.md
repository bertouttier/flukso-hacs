## Flukso

This custom component allows you to add [Flukso](https://flukso.net/) energy monitoring devices over the local MQTT link.

This page describes how to integrate your Flukso energy monitoring devices with Home Assistant. Installation instructions for your Flukso device itself can be found on the [official website](https://flukso.net/installation).

## Requirements

- MQTT broker and the [MQTT integration](/integrations/mqtt/) set up in Home Assistant.
- MQTT bridge set up between your Flukso MQTT broker and your Home Assistant MQTT Broker.

## Supported Features

Both Flukso sensors and [Kube](https://www.flukso.net/files/presentations/flukso.20140424.pdf) sensors are supported. Multiple Flukso's are supported.

## Installation

If using the [Mosquitto Broker add-on for Home Assistant](https://github.com/home-assistant/addons/blob/master/mosquitto/DOCS.md), you can add the following sample bridge configuration in your `customize` folder to set up a bridge connection to your Flukso MQTT broker:

`/share/mosquitto/acl.conf`:
```ini
acl_file /share/mosquitto/accesscontrollist
```

`/share/mosquitto/accesscontrollist.conf`:
```ini
topic readwrite #
```

`/share/mosquitto/flukso01.conf`:
```ini
connection flukso01
address <flukso ip>:1883
remote_clientid flukso01bridge
cleansession true
restart_timeout 5
topic # in 0
```

If you use another set up for your Home Assistant MQTT broker, please check its documentation to know how to set up a MQTT bridge to your Flukso MQTT broker.