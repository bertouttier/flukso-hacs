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

## Configuration

After setting up the MQTT bridge between your Home Assistant broker and your Flukso broker(s), and after installing this integration using HACS, we can start configuring your Flukso device(s).

First, you need to figure out your device (NOT sensor) hash value. Every Flukso device has 1 unique device hash. For this, you need to connect an MQTT client to your Home assistant MQTT broker (e.g. [MQTT explorer](http://mqtt-explorer.com)) and subscribe to topic `/device/#`. You will see MQTT topics in the form of `/device/<device hash>/config/<something>`. This is your device hash.

Use this value when setting up the [Flukso integration in your Home Assistant instance](https://my.home-assistant.io/redirect/config_flow_start/?domain=flukso). The integration will then automatically discover and add all your sensors to Home Assistant.