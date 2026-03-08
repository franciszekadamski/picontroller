import socket

import device_creation
import network_tools


CONFIGURATION_FILE_PATH = 'configuration.json'
IP_FILE_PATH = 'board_ip.json'


def setup_server_socket(board_ip: str) -> socket.socket:
    server = network_tools.NetworkServer(CONFIGURATION_FILE_PATH, board_ip)
    socket_conn = server.setup()
    socket_conn.settimeout(1.0)
    return socket_conn

def initialize_runtime() -> tuple[socket.socket, dict, str]:
    board_ip = device_creation.read_ip(IP_FILE_PATH)
    network_setup = setup_server_socket(board_ip)
    devices = device_creation.create_devices(CONFIGURATION_FILE_PATH, board_ip)
    return network_setup, devices, board_ip

def main() -> None:
    network_setup, devices, board_ip = initialize_runtime()
    
    while True:
        for device in devices.values():
            device.update_states()
        
        try:
            connection, _ = network_setup.accept()
        except socket.timeout:
            continue
        except OSError as e:
            print(f'Socket error: {e}')
            network_setup.close()
            network_setup = setup_server_socket(board_ip)
            continue
        
        try:
            data: bytes = connection.recv(1024)
            if not data:
                connection.close()
                continue
            try:
                device_name: str
                command: str
                device_name, command = data.decode().strip().split(':', 1)
            except ValueError as e:
                print(f'Invalid command format: {data.decode()} - {e}')
                connection.send(f'ERROR:Invalid command format'.encode())
                connection.close()
                continue
            
            if device_name not in devices:
                print(f'Unknown device: {device_name}')
                connection.send(f'ERROR:Unknown device {device_name}'.encode())
                connection.close()
                continue
            
            returned_value: str = devices[device_name](command)
            message: str = f'{device_name}:{returned_value}'
            connection.send(message.encode())
            
        except Exception as e:
            print(f'Error processing request: {e}')
        finally:
            connection.close()

if __name__ == '__main__':
    main()
