import network
import time
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

    # 0xa11140 is a magic hex to disable power saving on the CYW43 chip
    wlan.config(pm=0xa11140)

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

