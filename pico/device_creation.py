import json
import typing

import pico
import devices


DEVICE_TYPES: list[str] = ['sensor', 'servo', 'builtinled']


def create_single_device(device_description: typing.Mapping[str, typing.Any]) -> pico.devices.Device:
    if device_description['type'] not in DEVICE_TYPES:
        raise Exception(f'unsuported device type: {device_description["type"]}')
    if device_description['type'] == 'sensor':
        device = devices.Sensor(device_description)
    elif device_description['type'] == 'servo':
        device = devices.Servo(device_description)
    elif device_description['type'] == 'builtinled':
        device = devices.BuiltinLED(device_description)
    return device

def create_devices(file_path: str, board_ip: str) -> typing.Dict[str, pico.devices.Device]:
    with open(file_path, 'r') as file:
        device_descriptions: typing.Sequence[typing.Mapping[str, typing.Any]] = json.loads(file.read())['boards'][board_ip]
    devices: typing.Dict[str, pico.devices.Device] = {}
    for device_description in device_descriptions:
        device = create_single_device(device_description)
        name: str = device_description['name']
        devices[name] = device
    return devices

def read_ip(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return json.loads(file.read())['board_ip']
