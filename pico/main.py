import machine
import network
import utime
import time
import sys
import socket

from device_creation import create_devices, read_ip
from network_tools import setup_network_connection


# configuration.json and board_ip.json files are created
# and copied to the board manually
CONFIGURATION_FILE_PATH = 'configuration.json'
IP_FILE_PATH = 'board_ip.json'

board_ip = read_ip(IP_FILE_PATH)
s = setup_network_connection(CONFIGURATION_FILE_PATH, board_ip)
devices = create_devices(CONFIGURATION_FILE_PATH, board_ip)

while True:
    for device in devices.values():
        device.update_states()

    try:
        connection, address = s.accept()
        data = connection.recv(1024)
    except:
        s.close()
        s = setup_network_connection(CONFIGURATION_FILE_PATH, board_ip)
        continue
    if data:
        try:
            device_name, command = data.decode().strip().split(':')
        except Exception as e:
            print(f'{e}\n{data.decode()}')
            continue
        returned_value = devices[device_name](command)
        message = f'{device_name}:{returned_value}'
        connection.send(message.encode())
    connection.close()
