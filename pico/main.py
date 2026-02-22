import pico
import time
import socket

import device_creation
import network_tools


# configuration.json and board_ip.json files are created
# and copied to the board manually
CONFIGURATION_FILE_PATH = 'configuration.json'
IP_FILE_PATH = 'board_ip.json'


def setup_socket(board_ip: str) -> socket.socket:
    """Create and configure network server socket"""
    server = network_tools.NetworkServer(CONFIGURATION_FILE_PATH, board_ip)
    socket_conn = server.setup()
    socket_conn.settimeout(1.0)
    return socket_conn

def configuration_settings() -> tuple[socket.socket, dict[str, pico.devices.Device], str]:
    board_ip = device_creation.read_ip(IP_FILE_PATH)
    network_setup = setup_socket(board_ip)
    devices = device_creation.create_devices(CONFIGURATION_FILE_PATH, board_ip)
    return network_setup, devices, board_ip

def main():
    network_setup, devices, board_ip = configuration_settings()
    
    while True:
        # Update all device states periodically
        for device in devices.values():
            device.update_states()
        
        try:
            connection, _ = network_setup.accept()
        except socket.timeout:
            # Timeout allows loop to continue and update devices
            continue
        except OSError as e:
            # Handle socket errors by recreating connection
            print(f'Socket error: {e}')
            network_setup.close()
            network_setup = setup_socket(board_ip)
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
