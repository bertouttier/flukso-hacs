
DEVICE_HASH = "0123456789abcdef0123456789abcdef"

FLM03_FLX_CONFIG = {
    "1": {
        "enable": 1,
        "class": "ct",
        "name": "Zonnepanelen",
        "shift": 3,
        "current": 50
    },
    "3": {"shift": 0, "current": 50, "enable": 0, "class": "ct"},
    "main": {"led_mode": 255, "phase": "1p", "math": "p2+p1"},
    "2": {"enable": 1, "class": "ct", "name": "L1", "shift": 3, "current": 50},
    "5": {
        "enable": 1,
        "class": "pulse",
        "name": "gas",
        "constant": 0.1,
        "trigger": "edge"
    },
    "4": {
        "enable": 1,
        "class": "pulse",
        "name": "water",
        "constant": 1,
        "trigger": "edge"
    },
    "7": {
        "uart_tx_invert": 0,
        "enable": 0,
        "class": "uart",
        "dsmr": 4,
        "uart_rx_invert": 0
    },
    "6": {"trigger": "edge", "constant": 1, "enable": 0, "class": "pulse"}
}

FLM03_KUBE_CONFIG = {
    "1": {
        "enable": 1,
        "name": "keuken",
        "hw_type": 19218,
        "hw_id": "27600509030445ae75422e54031900f5",
        "sw_version": 1
    },
    "3": {
        "enable": 1,
        "name": "overloop",
        "hw_type": 19218,
        "hw_id": "14400409030445ae3e2b2e54001900f5",
        "sw_version": 1
    },
    "2": {
        "enable": 1,
        "name": "living",
        "hw_type": 19218,
        "hw_id": "2c800609030445aec2412e54041900f5",
        "sw_version": 1
    },
    "5": {
        "enable": 1,
        "sw_version": 1,
        "hw_type": 19218,
        "hw_id": "48c00304030445ae81122d54031900f5",
        "name": "kelder"
    },
    "4": {
        "enable": 1,
        "name": "slaapkamer",
        "hw_type": 19218,
        "hw_id": "13300404030445aefb002d54061900f5",
        "sw_version": 1
    },
    "7": {
        "enable": 1,
        "name": "berging",
        "hw_type": 19218,
        "hw_id": "30c00304030445ae4a0e2d54031900f5",
        "sw_version": 1
    },
    "6": {
        "enable": 1,
        "name": "ellis",
        "hw_type": 19218,
        "hw_id": "2cf00509030445ae45412e54011900f5",
        "sw_version": 1
    },
    "9": {
        "enable": 1,
        "sw_version": 1,
        "hw_type": 19218,
        "hw_id": "53b00304030445aef5112d54071900f5",
        "name": "midden"
    },
    "8": {
        "enable": 1,
        "sw_version": 1,
        "hw_type": 19218,
        "hw_id": "42b00304030445aede102d54061900f5",
        "name": "bureau"
    },
    "main": {
        "encryption": 0,
        "max_nodes": 30,
        "pair_group": 212,
        "null_key": "0123456789abcdef0123456789abcdef",
        "cache": "/usr/share/kube",
        "collect_group": 141,
        "key": "8387035a4756d60bd40313ff186c2526"
    }
}

FLM03_SENSOR_CONFIG = {
    "53": {
        "id": "4d418f8149203518274a4fefd3c4de43",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "movement"
    },
    "43": {
        "id": "183837ba8cb9175abfc11e21094935c6",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "gauge",
        "type": "pressure"
    },
    "73": {
        "id": "c0fae2f4c224502f36ab9ee6c952a385",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "gauge",
        "type": "temperature"
    },
    "63": {
        "id": "ec56f41ecb94e7764c196def930b01cc",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "counter",
        "type": "vibration"
    },
    "93": {
        "id": "02e596aa89d5344e68a13435f63d52b7",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "light"
    },
    "83": {
        "id": "eb16b48a6fb5e4ad6b93f3209feec5b3",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "error"
    },
    "13": {
        "type": "electricity",
        "subtype": "pplus",
        "id": "d5fec1970bd1d88d029116f21cb03c79",
        "enable": 1,
        "tmpo": 1,
        "rid": 0,
        "port": [2],
        "data_type": "counter"
    },
    "33": {
        "type": "electricity",
        "subtype": "pf",
        "enable": 0,
        "tmpo": 0,
        "id": "6f481ed92e08f85bb3ce5604384cb58f",
        "port": [3],
        "data_type": "gauge"
    },
    "23": {
        "type": "electricity",
        "subtype": "ithd",
        "id": "4f855ee38199793d46d00804a3cffdae",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "gauge"
    },
    "42": {
        "id": "d3e903b6c46bed83767114c5b6701ab2",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "gauge",
        "type": "battery"
    },
    "52": {
        "id": "f57e9d3bb49005f265ee49b09d8db5a9",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "pressure"
    },
    "62": {
        "id": "cd638a3cce5b5c8c01aefbeaae4da14d",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "counter",
        "type": "movement"
    },
    "72": {
        "id": "78f5177478096bba93a0df53ab46f5e8",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "counter",
        "type": "vibration"
    },
    "82": {
        "id": "5a0213afa9e3c4228f481449ef107a4f",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "temperature"
    },
    "92": {
        "id": "5cb0f5ad8b964cebae783d5c7820eb1d",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "error"
    },
    "122": {"id": "9181b8fd1d5e1fea32f7df8be42a8019"},
    "121": {"id": "3e6194dc4327a2986ac3d51ce2d97cf4"},
    "main": {"max_provisioned_sensors": 128},
    "12": {
        "type": "electricity",
        "subtype": "alpha",
        "enable": 0,
        "tmpo": 0,
        "id": "e466e2959c9a849bf538b736c7f2d7c1",
        "port": [1],
        "data_type": "gauge"
    },
    "22": {
        "type": "electricity",
        "subtype": "vthd",
        "id": "26a82ad6683bbc3ff95f0d910e64650b",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "gauge"
    },
    "32": {
        "type": "electricity",
        "subtype": "irms",
        "enable": 0,
        "tmpo": 0,
        "id": "f258a2a792de782f33dc5c45ec7d464d",
        "port": [3],
        "data_type": "gauge"
    },
    "95": {
        "id": "dba422a31164b349f558d6f632108794",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "humidity"
    },
    "85": {
        "id": "3e212ba38a095ea6eac31b19ed2cd0fe",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "proximity"
    },
    "75": {
        "id": "5540e22910e6d5ba6f86cf5d549d1185",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "gauge",
        "type": "light"
    },
    "65": {
        "id": "78147d351fc6aa0ef6bbec635b4f4882",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "gauge",
        "type": "error"
    },
    "55": {
        "id": "7480822ced69666845caec4dfbedcb2b",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "temperature"
    },
    "45": {
        "id": "178c9f4d2a98151f343a67217d578c4d",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "counter",
        "type": "vibration"
    },
    "35": {
        "type": "electricity",
        "subtype": "ithd",
        "enable": 0,
        "tmpo": 0,
        "id": "8109767826519521299f5a34c3e76a63",
        "port": [3],
        "data_type": "gauge"
    },
    "116": {
        "id": "63ad6c9a3bd7bc6363b725e85869b8b8",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "movement"
    },
    "1": {
        "type": "electricity",
        "subtype": "pplus",
        "id": "3e41db71f8536f0cd05cc4de26124daa",
        "tmpo": 1,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "counter"
    },
    "3": {
        "type": "electricity",
        "subtype": "q1",
        "id": "58e09e396968b58f8cc2f865456a3834",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "counter"
    },
    "2": {
        "type": "electricity",
        "subtype": "pminus",
        "id": "a6e1d91377c11d38cb248a27ef2b9f67",
        "tmpo": 1,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "counter"
    },
    "5": {
        "type": "electricity",
        "subtype": "q3",
        "id": "3c782b53018296a8bfa1e6faac473e66",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "counter"
    },
    "4": {
        "type": "electricity",
        "subtype": "q2",
        "id": "7711ee09da56dc06c6cf70ca33f655cb",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "counter"
    },
    "7": {
        "type": "electricity",
        "subtype": "vrms",
        "id": "3c8367a30fe628103b92a26cf93e6d19",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "gauge"
    },
    "6": {
        "type": "electricity",
        "subtype": "q4",
        "id": "2edba0b1fca700c8375977cdb565a7bb",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "counter"
    },
    "9": {
        "type": "electricity",
        "subtype": "pf",
        "id": "12652edace9590f31665f1033624663d",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "gauge"
    },
    "15": {
        "type": "electricity",
        "subtype": "q1",
        "id": "228dd2eccc91976ffc3b6047561bfb8f",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "counter"
    },
    "110": {
        "id": "23a39c2fee8fb23fb0a7310bb1078f0b",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "error"
    },
    "94": {
        "id": "0230d30e4acbdb244246fb091ffab4e5",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "proximity"
    },
    "74": {
        "id": "30869a51efc3983c1566e0ab0631e706",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "gauge",
        "type": "error"
    },
    "84": {
        "id": "53ffb6bbe26ecb747a1ae6b8502a0d29",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "light"
    },
    "54": {
        "id": "8c6cd0b4c10f8804b34f824d8b22ce6a",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "vibration"
    },
    "64": {
        "id": "28cc6a8f683fd1a7cc3a2cc973401d1d",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "gauge",
        "type": "temperature"
    },
    "34": {
        "type": "electricity",
        "subtype": "vthd",
        "enable": 0,
        "tmpo": 0,
        "id": "434d00ec7854a3f061be56b5449800fe",
        "port": [3],
        "data_type": "gauge"
    },
    "44": {
        "id": "b912c42856631681ff4824865622573b",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "counter",
        "type": "movement"
    },
    "126": {"id": "a26a2744bc9158395aeb908b799bdb58"},
    "102": {
        "id": "0a6f4298ada617d13c06e3174e1e3ec8",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "light"
    },
    "101": {
        "id": "49f11b6ac2bccbc88ad87d588514721b",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "error"
    },
    "14": {
        "type": "electricity",
        "subtype": "pminus",
        "id": "6f90fe00444a573c5e2532d24a302057",
        "enable": 1,
        "tmpo": 1,
        "rid": 0,
        "port": [2],
        "data_type": "counter"
    },
    "24": {
        "type": "electricity",
        "subtype": "alpha",
        "enable": 0,
        "tmpo": 0,
        "id": "211926dbe09d18783e2137040a7f1ce3",
        "port": [2],
        "data_type": "gauge"
    },
    "128": {"id": "495947c8b78d49b502d3c6bd6893d1da"},
    "120": {
        "id": "32220a38a41ad1dfacb3f3ee9ed9921a",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "light"
    },
    "87": {
        "id": "3844a85bbcaa84235dc9b27129a7118f",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "battery"
    },
    "77": {
        "id": "fd1505551188671579368cf76a21b6b2",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "humidity"
    },
    "97": {
        "id": "fd0cb4e37c59d82bb095ff512a2ac7c6",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "pressure"
    },
    "47": {
        "id": "e9fc028f13ecca73d5ba0a9ef2312a0b",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "gauge",
        "type": "error"
    },
    "37": {
        "id": "b620c48665f630b4e0b42a3afa503f40",
        "tmpo": 1,
        "type": "water",
        "rid": 0,
        "enable": 1,
        "data_type": "counter",
        "port": [4]
    },
    "67": {
        "id": "4052d3c6d44103324e1c35abadd0dd52",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "counter",
        "type": "proximity"
    },
    "57": {
        "id": "97bdc37b5d58ba5d03255786afb5d70e",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "light"
    },
    "112": {
        "id": "918a401e3d2b21ab600e1099f92a7d38",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "proximity"
    },
    "tmpo": {"decimate": 8, "root": "/flukso/"},
    "115": {
        "id": "afa3dfd3d062edb21e47c206c081e355",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "pressure"
    },
    "111": {
        "id": "285fa2f6a04c0e7db88fb4e76baeb3bd",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "light"
    },
    "114": {
        "id": "b6cdeabd42cbd1d8e9260cd64fb48fb5",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "battery"
    },
    "119": {
        "id": "c85c3c3cc6276a76d58e72cc780dda36",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "error"
    },
    "27": {
        "type": "electricity",
        "subtype": "q1",
        "enable": 0,
        "tmpo": 0,
        "id": "906b07f699f3f7d3f2d50ecb811113a8",
        "port": [3],
        "data_type": "counter"
    },
    "17": {
        "type": "electricity",
        "subtype": "q3",
        "id": "4445bf709045b308a08ece0671ebfe07",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "counter"
    },
    "76": {
        "id": "feede991583c8d9d2cc61a592d18d77a",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "proximity"
    },
    "86": {
        "id": "e0cb7605fd15d7ad222f8daa289c5b1d",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "humidity"
    },
    "96": {
        "id": "94432ed8100e22db311e2177a1394cc6",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "battery"
    },
    "36": {
        "type": "electricity",
        "subtype": "alpha",
        "enable": 0,
        "tmpo": 0,
        "id": "022cd297f49003a6c1ab28f6820fdf12",
        "port": [3],
        "data_type": "gauge"
    },
    "46": {
        "id": "c9af7cf6203160ceec5452ac84a3645b",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "gauge",
        "type": "temperature"
    },
    "103": {
        "id": "27dc32e28e8e9c2c6a7d18a57717560b",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "proximity"
    },
    "66": {
        "id": "a6c80b3ddca75e67a827c94c6f0fdda9",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "gauge",
        "type": "light"
    },
    "106": {
        "id": "e914e15adb85106425b690b68611d011",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "pressure"
    },
    "125": {"id": "1711d807afdb333cd536d16b9f86219a"},
    "108": {
        "id": "1f44068ab26057e137cf8bad41f56298",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "vibration"
    },
    "124": {"id": "efe8117166b8b9f28d9f1d6bcaf6e13a"},
    "16": {
        "type": "electricity",
        "subtype": "q2",
        "id": "f4a4505b14d2c3f480825a38bae85487",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "counter"
    },
    "26": {
        "type": "electricity",
        "subtype": "pminus",
        "enable": 0,
        "tmpo": 1,
        "id": "ecc4a082d472cc93237e9e7c953b1941",
        "port": [3],
        "data_type": "counter"
    },
    "100": {
        "id": "9f5a1eb7322ba874214464aac4bcea3b",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "temperature"
    },
    "71": {
        "id": "ef1455f01447f772f9843034d5c571f4",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "counter",
        "type": "movement"
    },
    "61": {
        "id": "acac49a0f5d05b483190fc84251e6bc2",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "gauge",
        "type": "pressure"
    },
    "51": {
        "id": "a21b3b5fa1274c1002427b8115924b29",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "battery"
    },
    "mqtt": {
        "bridge_restart_timeout": 30,
        "bridge_address": "api.flukso.net",
        "bridge_port": 8883,
        "bridge_keepalive": 60
    },
    "91": {
        "id": "ca76091f580d86a37120e09ee65e89fd",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "temperature"
    },
    "81": {
        "id": "4dc9627eb39a63d1145bebefbdeba39e",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "vibration"
    },
    "59": {
        "id": "ce2aa65c83080c07cfe3c73b31e72366",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "gauge",
        "type": "humidity"
    },
    "49": {
        "id": "9adc1654c38740c11b72428a08a09c58",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "proximity"
    },
    "39": {
        "type": "electricity",
        "subtype": "pplus",
        "enable": 0,
        "tmpo": 1,
        "id": "a54a7f79abf96d30c046ee63c75fc6bd",
        "port": [6],
        "data_type": "counter"
    },
    "29": {
        "type": "electricity",
        "subtype": "q3",
        "enable": 0,
        "tmpo": 0,
        "id": "28b239c15fe9bde85a680b4604ca9eca",
        "port": [3],
        "data_type": "counter"
    },
    "99": {
        "id": "019bd5b31d85461a73c09c6203d70eac",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "vibration"
    },
    "89": {
        "id": "8d79f65a673cf01cb617b3105b750379",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "movement"
    },
    "79": {
        "id": "ae5c1415034c841cd0bf19f668df3b11",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "pressure"
    },
    "69": {
        "id": "db80a0806102a16a23774d8ddb687f0f",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "gauge",
        "type": "battery"
    },
    "19": {
        "type": "electricity",
        "subtype": "vrms",
        "id": "7ee001173401b41e359177b7e6768736",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "gauge"
    },
    "31": {
        "type": "electricity",
        "subtype": "vrms",
        "enable": 0,
        "tmpo": 0,
        "id": "7fc35601b62c46478c62b4f55dab49bb",
        "port": [3],
        "data_type": "gauge"
    },
    "21": {
        "type": "electricity",
        "subtype": "pf",
        "id": "ab3b8f6b5f320b006c2c3e2368a33d35",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "gauge"
    },
    "11": {
        "type": "electricity",
        "subtype": "ithd",
        "id": "ad110564cad9703529746073082bc074",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "gauge"
    },
    "60": {
        "id": "f3ac34dc969fcbcbc63cf7021c706521",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "gauge",
        "type": "battery"
    },
    "70": {
        "id": "8d46c048f63da3075c91d51ca35a7c62",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "gauge",
        "type": "pressure"
    },
    "40": {
        "id": "c308b0a71b8c37dfd57dd381328f9304",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "counter",
        "type": "proximity"
    },
    "50": {
        "id": "36a2a7daf697f0e18dd7f2015ef2e882",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "humidity"
    },
    "127": {"id": "eb3a5900c6cffabf1b2afeb6ce76d964"},
    "123": {"id": "cd246837f5ca3523ef7f9cb88cdafcfa"},
    "80": {
        "id": "decf9fa093b273cb0230674503f11756",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "movement"
    },
    "90": {
        "id": "3b3e4fd10b1814989663b4731eefb785",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "vibration"
    },
    "48": {
        "id": "1779dd0685d51060fde1c21338b857f0",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "gauge",
        "type": "light"
    },
    "58": {
        "id": "799d0b1d20d0cd518d952cd623050739",
        "class": "kube",
        "kid": 3,
        "enable": 1,
        "rid": 1,
        "data_type": "counter",
        "type": "proximity"
    },
    "28": {
        "type": "electricity",
        "subtype": "q2",
        "enable": 0,
        "tmpo": 0,
        "id": "5d2e5a8cf9318eddefcc2573ed77af09",
        "port": [3],
        "data_type": "counter"
    },
    "38": {
        "id": "58f44d69532bafa2777737318c388885",
        "tmpo": 1,
        "type": "gas",
        "rid": 0,
        "enable": 1,
        "data_type": "counter",
        "port": [5]
    },
    "88": {
        "id": "735185e014a0be16b4ae5b80f7e8a0ac",
        "class": "kube",
        "kid": 6,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "pressure"
    },
    "98": {
        "id": "1b9208b9258bcb2ee8032ada8cac9535",
        "class": "kube",
        "kid": 7,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "movement"
    },
    "68": {
        "id": "a53d989b6dce316ad93ae19e71a54086",
        "class": "kube",
        "kid": 4,
        "enable": 1,
        "rid": 9,
        "data_type": "gauge",
        "type": "humidity"
    },
    "78": {
        "id": "1eaf4e3a227133c680aacb62fe2599bb",
        "class": "kube",
        "kid": 5,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "battery"
    },
    "109": {
        "id": "8db7b760210b7e660812d2f768575485",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "temperature"
    },
    "118": {
        "id": "79ee93cc7d9f7e247f8ac379cc9a525e",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "temperature"
    },
    "105": {
        "id": "8b19b57de1376f3f0c3e75e1977dd4d6",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "battery"
    },
    "117": {
        "id": "198bdd56e9007252336e661975859b3d",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "vibration"
    },
    "113": {
        "id": "ec5ab3ccf2ac6c9794fb726c7ae6742f",
        "class": "kube",
        "kid": 9,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "humidity"
    },
    "18": {
        "type": "electricity",
        "subtype": "q4",
        "id": "81a6e137a1cff34c3402fb08513f74d2",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "counter"
    },
    "56": {
        "id": "0e6b8797f40b4b3336b92c10e89689f8",
        "class": "kube",
        "kid": 2,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "error"
    },
    "107": {
        "id": "039d3b273dee3b556a3d13c1b9f2e4cb",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "counter",
        "type": "movement"
    },
    "8": {
        "type": "electricity",
        "subtype": "irms",
        "id": "4f771b1b9cea6359401f32979800b456",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "gauge"
    },
    "41": {
        "id": "00b88c8db363a0bd76d8ed395411cc9a",
        "class": "kube",
        "kid": 1,
        "enable": 1,
        "rid": 3,
        "data_type": "gauge",
        "type": "humidity"
    },
    "25": {
        "type": "electricity",
        "subtype": "pplus",
        "enable": 0,
        "tmpo": 1,
        "id": "6547a7d70044869acf5651ac09430315",
        "port": [3],
        "data_type": "counter"
    },
    "104": {
        "id": "6e180d5f66963bdf378c00964f2fb6ce",
        "class": "kube",
        "kid": 8,
        "enable": 1,
        "rid": 0,
        "data_type": "gauge",
        "type": "humidity"
    },
    "20": {
        "type": "electricity",
        "subtype": "irms",
        "id": "60cb378b4d2979428ebc4fdaa2611d51",
        "enable": 1,
        "tmpo": 0,
        "rid": 0,
        "port": [2],
        "data_type": "gauge"
    },
    "30": {
        "type": "electricity",
        "subtype": "q4",
        "enable": 0,
        "tmpo": 0,
        "id": "8684a5246cd7f55a3ea67aec2bce8ec1",
        "port": [3],
        "data_type": "counter"
    },
    "10": {
        "type": "electricity",
        "subtype": "vthd",
        "id": "2c977b4391e5af8a0547e775b3277308",
        "tmpo": 0,
        "enable": 1,
        "rid": 0,
        "port": [1],
        "data_type": "gauge"
    },
    "daemon": {
        "cacert": "/etc/ssl/certs/flukso.ca.crt",
        "upgrade_url": "http://www.flukso.net/files/upgrade/",
        "wan_base_url": "https://api.flukso.net/"
    }
}

FLM03_TAP_CONFIG = """
1..12
# date: Mon, 20 Sep 2021 10:19:33 +0000
# serial: FL01234567
# firmware: 380
ok 1 - flxd daemon running
ok 2 - sensor board communication
ok 3 - /flukso/tmpo dir present
ok 4 - serial number loaded
ok 5 - sensor config loaded
not ok 6 - wifi connection
ok 7 - ping flukso.net
ok 8 - api.flukso.net tcp port 22 [ssh]
ok 9 - api.flukso.net tcp port 80 [http]
ok 10 - api.flukso.net tcp port 443 [https]
ok 11 - api.flukso.net tcp port 8883 [mqtt/ssl]
ok 12 - 0.openwrt.pool.ntp.org udp port 123 [ntp]

"""

FLM02_SENSOR_CONFIG = {
    "mqtt": {
        "bridge_restart_timeout": 30,
        "bridge_address": "api.flukso.net",
        "bridge_port": 8883,
        "bridge_keepalive": 60
    },
    "1": {
        "id": "",
        "class": "analog",
        "type": "electricity",
        "function": "L - FLM02",
        "port": [
            1
        ],
        "enable": 1,
        "rid": 0,
        "current": 50,
        "data_type": "counter",
        "voltage": 230
    },
    "10": {
        "id": ""
    },
    "3": {
        "enable": 0,
        "class": "analog",
        "port": [
            3
        ],
        "id": "",
        "current": 50,
        "type": "electricity",
        "voltage": 230
    },
    "2": {
        "enable": 0,
        "class": "analog",
        "port": [
            2
        ],
        "id": "",
        "current": 50,
        "type": "electricity",
        "voltage": 230
    },
    "5": {
        "enable": 0,
        "class": "pulse",
        "constant": 1,
        "port": [
            5
        ],
        "id": "",
        "type": "electricity"
    },
    "4": {
        "enable": 0,
        "class": "pulse",
        "constant": 1,
        "port": [
            4
        ],
        "id": "",
        "type": "electricity"
    },
    "7": {
        "id": ""
    },
    "6": {
        "id": "",
        "port": [
            6
        ],
        "enable": 0,
        "class": "uart"
    },
    "9": {
        "id": ""
    },
    "8": {
        "id": ""
    },
    "main": {
        "reset_counters": 0,
        "dsmr": 4,
        "max_sensors": 6,
        "sw_major": 1,
        "max_provisioned_sensors": 13,
        "led_mode": 256,
        "uart_tx_invert": 0,
        "phase": 1,
        "hw_major": 2,
        "hw_minor": 1,
        "max_analog_sensors": 3,
        "sw_minor": 0,
        "uart_rx_invert": 0
    },
    "fsync": {
        "time": 1501084187,
        "exit_string": "successful",
        "exit_status": 0
    },
    "13": {
        "id": ""
    },
    "12": {
        "id": ""
    },
    "11": {
        "id": ""
    },
    "daemon": {
        "upgrade_url": "http://www.flukso.net/files/upgrade/",
        "enable_wan_branch": 1,
        "cacert": "/etc/ssl/certs/flukso.ca.crt",
        "enable_remote_upgrade": 1,
        "wan_base_url": "https://api.flukso.net/",
        "enable_lan_branch": 1,
        "logmask": "info"
    }
}
