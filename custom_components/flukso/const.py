"""Constants for the Flukso integration."""

DOMAIN = "flukso"

CONF_DEVICE_HASH = "device_hash"

# Seconds to wait for the retained sensor config after subscribing.
CONFIG_TIMEOUT = 10
# Seconds to wait for the optional kube/flx configs and the FLM03 TAP report.
OPTIONAL_CONFIG_TIMEOUT = 2
# Seconds before a kube movement/vibration binary sensor turns off again.
MOTION_OFF_DELAY = 10
