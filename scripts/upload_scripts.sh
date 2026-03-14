#!/usr/bin/bash

mpremote fs cp "${1}/main.py" :main.py
mpremote fs cp "${1}/devices.py" :devices.py
mpremote fs cp "${1}/device_creation.py" :device_creation.py
mpremote fs cp "${1}/network_tools.py" :network_tools.py
mpremote fs cp "${1}/robust.py" :robust.py
mpremote fs cp "${1}/simple.py" :simple.py
