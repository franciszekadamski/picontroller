import network
import time
import socket
import json


class NetworkServer:
    def __init__(self, config_path: str, board_ip: str, port: int = 1234):
        self._load_configuration(config_path, board_ip)
        self.port = port
        self.socket = None

    def _load_configuration(self, config_path: str, board_ip: str):
        """Load network configuration from file"""
        with open(config_path, 'r') as file:
            self._data = json.loads(file.read())['network']
        self.ssid = self._data['ssid']
        self.password = self._data['password']
        self.ip = board_ip
        self.subnet = self._data['subnet']
        self.gateway = self._data['gateway']
        self.dns = self._data['dns']

    def connect(self):
        """Connect to WiFi network"""
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        wlan.ifconfig(
            (
                self.ip,
                self.subnet,
                self.gateway,
                self.dns
            )
        )

        wlan.connect(self.ssid, self.password)

        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            print("Connecting...")
            time.sleep(1)
            max_wait -= 1

        if wlan.isconnected():
            print("Connected! IP:", wlan.ifconfig()[0])
        else:
            print("Failed to connect")

    def create_socket(self):
        """Create and bind socket"""
        address = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]

        while True:
            try:
                s = socket.socket()
                s.settimeout(10.0)
                s.bind(address)
                s.listen(1)
                print('Listening on', address)
                self.socket = s
                return s
            except:
                print('could not bind to the address, retrying')
                time.sleep(1)

    def setup(self):
        """Setup network connection and create socket"""
        self.connect()
        return self.create_socket()


# Backward compatibility function
def setup_network_connection(path: str, board_ip: str):
    """Legacy function - use NetworkServer directly instead"""
    server = NetworkServer(path, board_ip)
    return server.setup()

