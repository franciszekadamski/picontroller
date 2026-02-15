import pico
import time
import sys
import socket

import device_creation
import network_tools


# configuration.json and board_ip.json files are created
# and copied to the board manually
CONFIGURATION_FILE_PATH = 'configuration.json'
IP_FILE_PATH = 'board_ip.json'


def configuration_settings() -> tuple[socket.socket, dict[str, pico.devices.Device], str]:
    board_ip = device_creation.read_ip(IP_FILE_PATH)
    network_setup = network_tools.setup_network_connection(CONFIGURATION_FILE_PATH, board_ip)
    devices = device_creation.create_devices(CONFIGURATION_FILE_PATH, board_ip)
    return network_setup, devices, board_ip

def main():
    network_setup, devices, board_ip = configuration_settings()
    network_setup.settimeout(1.0)  # Set timeout to allow periodic device updates
    
    while True:
        # Update all device states periodically
        for device in devices.values():
            device.update_states()
        
        try:
            connection, address = network_setup.accept()
        except socket.timeout:
            # Timeout allows loop to continue and update devices
            continue
        except OSError as e:
            # Handle socket errors by recreating connection
            print(f'Socket error: {e}')
            network_setup.close()
            network_setup = network_tools.setup_network_connection(CONFIGURATION_FILE_PATH, board_ip)
            network_setup.settimeout(1.0)
            continue
        
        try:
            data = connection.recv(1024)
            if not data:
                continue
            
            # Parse command
            try:
                device_name, command = data.decode().strip().split(':', 1)
            except ValueError as e:
                print(f'Invalid command format: {data.decode()} - {e}')
                connection.close()
                continue
            
            # Validate device exists
            if device_name not in devices:
                print(f'Unknown device: {device_name}')
                connection.send(f'ERROR:Unknown device {device_name}'.encode())
                connection.close()
                continue
            
            # Execute command
            returned_value = devices[device_name](command)
            message = f'{device_name}:{returned_value}'
            connection.send(message.encode())
            
        except Exception as e:
            print(f'Error processing request: {e}')
        finally:
            connection.close()

if __name__ == '__main__':
    main()
