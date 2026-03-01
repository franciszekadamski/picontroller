import json
import typing

import devices


DEVICE_TYPES: list[str] = ['sensor', 'servo', 'builtinled']
DEVICE_CLASS_MAP: dict[str, type[devices.Device]] = {
    'sensor': devices.Sensor,
    'servo': devices.Servo,
    'builtinled': devices.BuiltinLED,
}

def create_single_device(device_description: typing.Mapping[str, typing.Any]) -> devices.Device:
    if device_description['type'] not in DEVICE_TYPES:
        raise ValueError(f'unsupported device type: {device_description["type"]}')
    device_type = device_description['type']
    return DEVICE_CLASS_MAP[device_type](device_description)

def create_devices(file_path: str, board_ip: str) -> typing.Dict[str, devices.Device]:
    with open(file_path, 'r') as file:
        device_descriptions: typing.Sequence[typing.Mapping[str, typing.Any]] = json.loads(file.read())['boards'][board_ip]
    created_devices: typing.Dict[str, devices.Device] = {}
    for device_description in device_descriptions:
        device = create_single_device(device_description)
        name: str = device_description['name']
        created_devices[name] = device
    return created_devices

def read_ip(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return json.loads(file.read())['board_ip']
