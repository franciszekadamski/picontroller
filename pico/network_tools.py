import network
import time
import socket
import json


class NetworkConfiguration:
    def __init__(self, path: str, board_ip: str):
        with open(path, 'r') as file:
            self._data = json.loads(file.read())['network']
        self.ssid = self._data['ssid']
        self.password = self._data['password']
        self.ip = board_ip
        self.subnet = self._data['subnet']
        self.gateway = self._data['gateway']
        self.dns = self._data['dns']



def setup_network_connection(path: str, board_ip: str):
    network_configuration = NetworkConfiguration(path, board_ip)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.ifconfig(
        (
            network_configuration.ip,
            network_configuration.subnet,
            network_configuration.gateway,
            network_configuration.dns
        )
    )

    wlan.connect(
        network_configuration.ssid,
        network_configuration.password
    )

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


    address = socket.getaddrinfo('0.0.0.0', 1234)[0][-1]

    while True:
        try:
            s = socket.socket()
            s.settimeout(10.0)
            s.bind(address)
            s.listen(1)
            print('Listening on', address) 
            return s
        except:
            print('could not bind to the address, retrying')
            time.sleep(1)

