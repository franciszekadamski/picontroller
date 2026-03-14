import machine
import network
import utime
import time
import sys
import socket

from device_creation import create_devices, read_ip, read_hub_ip
from network_tools import setup_network_connection

from robust import MQTTClient


# configuration.json and board_ip.json files are created
# and copied to the board manually
CONFIGURATION_FILE_PATH = 'configuration.json'
IP_FILE_PATH = 'board_ip.json'
HUB_IP = read_hub_ip(CONFIGURATION_FILE_PATH)

BOARD_IP = read_ip(IP_FILE_PATH)
setup_network_connection(CONFIGURATION_FILE_PATH, BOARD_IP)
devices = create_devices(CONFIGURATION_FILE_PATH, BOARD_IP)

client = MQTTClient(BOARD_IP, HUB_IP, keepalive=60)

def sub_callback(topic, message):
    print(f'Received command: {topic} -> {message}')

    decoded_data = message.decode().strip()
    device_name, command = decoded_data.split(':')[:2]
    
    if device_name in devices:
        returned_value = devices[device_name](command)
        response_message = f'{device_name}:{returned_value}'
        client.publish(f'pico/{BOARD_IP}/response', response_message)
        print('response sent back to broker')
    else:
        client.publish(f'pico/{BOARD_IP}/response', 'error:device_not_found')
        print('response sent back to broker')

client.set_callback(sub_callback)

def connect_and_subscribe():
    try:
        print("Attempting to connect to MQTT...")
        client.connect()
        client.subscribe(f'pico/{BOARD_IP}/request')
        print("Connected and Subscribed!")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

connect_and_subscribe()

print('Ready for connections...')

while True:
    for device in devices.values():
        device.update_states()

    try:
        client.check_msg()
        time.sleep(0.05)

    except Exception as e:
        print(f"Critical error: {e}")
        time.sleep(1)
        setup_network_connection(CONFIGURATION_FILE_PATH, BOARD_IP)
        success = connect_and_subscribe()
        while not success:
            time.sleep(5)
            success = connect_and_subscribe()

