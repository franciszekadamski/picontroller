import json

from devices import Sensor, DHT11Sensor, Servo, BuiltinLED


DEVICE_TYPES = ['sensor', 'dht11_sensor', 'servo', 'builtinled']


def create_device(device_description: dict):
    if device_description['type'] not in DEVICE_TYPES:
        raise Exception(f'unsuported device type: {}')

    if device_description['type'] == 'sensor':
        device = Sensor(device_description)
    elif device_description['type'] == 'dht11_sensor':
        device = DHT11Sensor(device_description)
    elif device_description['type'] == 'servo':
        device = Servo(device_description)
    elif device_description['type'] == 'builtinled':
        device = BuiltinLED(device_description)

    return device


def create_devices(file_path: str, board_ip: str):
    with open(file_path, 'r') as file:
        device_descriptions = json.loads(file.read())['boards'][board_ip]
    devices = {}
    for device_description in device_descriptions:
        device = create_device(device_description)
        name = device_description['name']
        devices[name] = device
    return devices


def read_ip(file_path: str):
    with open(file_path, 'r') as file:
        return json.loads(file.read())['board_ip']
