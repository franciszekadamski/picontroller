#!/usr/bin/python3

import json
import socket
import time

import paho.mqtt.client as mqtt

class PicoBoard:
    def __init__(self, board_ip: str, mqtt_client: mqtt.Client):
        self.mqtt_client = mqtt_client
        self.last_response = None

        self.request_topic = f'pico/{board_ip}/request'
        self.response_topic = f'pico/{board_ip}/response'

        self.mqtt_client.message_callback_add(self.response_topic, self._on_msg)
        self.mqtt_client.subscribe(self.response_topic)


    def _on_msg(self, client, userdata, in_message):
        # if in_message.topic == self.response_topic:
        self.last_response = in_message.payload.decode().strip()

    def send(self, message: str, timeout=0.1):
        self.last_response = None

        try:
            self.mqtt_client.publish(self.request_topic, message, retain=False)

            start_time = time.time()
            while self.last_response is None:
                if time.time() - start_time > timeout:
                    return f'timeouterror-{message}'
                time.sleep(0.01)

            if ':' in self.last_response:
                device_name = self.last_response.split(':')[0]
                expected_device_name = message.split(':')[0]
                if device_name != expected_device_name:
                    return "error:wrong_device"
            else:
                return "error:no_delimiter"

            return self.last_response
        except Exception as e:
            print(f'error when sending: {e}')

        # finally:
            # self.mqtt_client.message_callback_remove(self.response_topic)


def read_board_ips(path: str):
    with open(path, 'r') as file:
        configuration = json.loads(file.read())
    return list(configuration['boards'].keys())


def create_boards(path: str, mqtt_client: mqtt.Client):
    board_ips = read_board_ips(path)
    boards = {}
    for board_ip in board_ips:
        boards[board_ip] = PicoBoard(board_ip, mqtt_client)

    return boards
