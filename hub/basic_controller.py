import datetime
import json
import time

import zmq

from boards import PicoBoard, create_boards


class BasicController:
    def __init__(self, configuration_file_path: str):
        self.boards = create_boards(configuration_file_path)
        with open(configuration_file_path, 'r') as file:
            configuration = json.loads(file.read())

        self.device_board_map = {}
        for board_ip, devices in configuration['boards'].items():
            for device in devices:
                device_name = device['name']
                self.device_board_map[device_name] = board_ip


        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.REP)
        self.zmq_socket.bind('tcp://*:5555')
        self.zmq_data_store = configuration['zmq_data_store']


    def send(self, message: str):
        device_name = message.split(':')[0]
        target_board_name = self.device_board_map[device_name]
        target_board = self.boards[target_board_name]
        answer = target_board.send(message)
        return answer


    def handle_zmq(self):
        try:
            message = self.zmq_socket.recv_json(flags=zmq.NOBLOCK)
            if message.get('action') == 'get':
                self.zmq_socket.send_json(self.zmq_data_store)
            elif message.get('action') == 'set':
                new_data = message.get('data', {})
                self.zmq_data_store.update(new_data)
                self.zmq_socket.send_json(self.zmq_data_store)
        except zmq.Again:
            pass


    def main_loop(self):
        while True:
            try:
                self.handle_zmq()
                self.main()
            except Exception as e:
                print(f'there was an error: {e}')
            finally:
                time.sleep(self.zmq_data_store['main_loop_sleep_time_s'])


    def main(self):
        answer = self.send('builtin_led:blink')
        print(answer)

