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

print("Ready for connections...")

while True:
    # 1. Update devices regardless of connection
    for device in devices.values():
        device.update_states()

    try:
        # Set a short timeout so we can still run device.update_states() 
        # while waiting for a new connection from the Pi
        s.settimeout(0.1) 
        connection, address = s.accept()
        print(f"Connected by {address}")
        connection.settimeout(5.0) # Connection-specific timeout
        
        # 2. Stay in this loop as long as the Pi is talking to us
        while True:
            try:
                data = connection.recv(1024)
                if not data:
                    break # Pi closed the connection gracefully
                
                # Process the command
                try:
                    decoded_data = data.decode().strip()
                    device_name, command = decoded_data.split(':')
                    
                    if device_name in devices:
                        returned_value = devices[device_name](command)
                        message = f'{device_name}:{returned_value}'
                        connection.send(message.encode())
                    else:
                        connection.send(b"error:device_not_found")
                except Exception as e:
                    print(f"Protocol error: {e}")
                    connection.send(b"error:bad_format")

            except OSError:
                # This usually means a timeout or a reset from the Pi side
                break 
                
        connection.close()
        print("Connection closed, waiting for new one...")

    except OSError:
        # This happens if s.accept() times out. 
        # We just loop back and check device.update_states() again.
        continue 
    except Exception as e:
        print(f"Critical error: {e}")
        # Only reset the server socket if it actually dies
        s.close()
        utime.sleep(1)
        s = setup_network_connection(CONFIGURATION_FILE_PATH, board_ip)

