import json
import logging
import time

import zmq

from boards import PicoBoard, create_boards


class BasicController:
    def __init__(self, configuration_file_path: str):
        self.logger = logging.getLogger(self.__class__.__name__)
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


    def send_device_command(self, message: str):
        try:
            device_name, _ = message.split(':', 1)
        except ValueError:
            self.logger.warning(f'Invalid command format: {message}')
            return 'ERROR:Invalid command format'

        target_board_name = self.device_board_map.get(device_name)
        if target_board_name is None:
            self.logger.warning(f'Unknown device in command: {device_name}')
            return f'ERROR:Unknown device {device_name}'

        target_board = self.boards.get(target_board_name)
        if target_board is None:
            self.logger.error(f'No board configured for IP: {target_board_name}')
            return f'ERROR:Unknown board {target_board_name}'

        try:
            answer = target_board.send(message)
            return answer
        except (OSError, TimeoutError, ConnectionError) as e:
            self.logger.error(f'Failed sending "{message}" to {target_board_name}: {e}')
            return f'ERROR:Board communication failed for {target_board_name}'


    def process_zmq_request(self):
        try:
            message = self.zmq_socket.recv_json(flags=zmq.NOBLOCK)
            if message.get('action') == 'get':
                self.zmq_socket.send_json(self.zmq_data_store)
            elif message.get('action') == 'set':
                new_data = message.get('data', {})
                self.zmq_data_store.update(new_data)
                self.zmq_socket.send_json(self.zmq_data_store)
            else:
                self.zmq_socket.send_json({'error': 'unknown action'})
        except zmq.Again:
            pass
        except (TypeError, ValueError, zmq.ZMQError) as e:
            self.logger.error(f'ZMQ handling error: {e}')


    def main_loop(self):
        while True:
            try:
                self.process_zmq_request()
                self.run_control_step()
            except (KeyError, TypeError, ValueError, OSError, zmq.ZMQError) as e:
                self.logger.error(f'Controller loop error: {e}')
            finally:
                time.sleep(self.zmq_data_store['main_loop_sleep_time_s'])


    def run_control_step(self):
        answer = self.send_device_command('builtin_led:blink')
        print(answer)

