#!/usr/bin/python3

import nclib
import json
import logging
import socket


class PicoBoard:
    def __init__(self, board_ip: str, board_port: int):
        self.ip = board_ip
        self.port = board_port


    def send(self, message: str):
        nc = None
        try:
            nc = nclib.Netcat((self.ip, self.port))
            nc.send(message.encode())
            answer = nc.recv(timeout=5)
            if not answer:
                return 'ERROR:Empty response from board'
            return answer.decode()
        except (socket.timeout, TimeoutError, OSError, UnicodeDecodeError) as e:
            logging.getLogger(__name__).error(f'Board communication error ({self.ip}:{self.port}): {e}')
            return f'ERROR:Board communication failed for {self.ip}'
        finally:
            if nc is not None:
                nc.close()


def get_board_ips_from_config(path: str):
    with open(path, 'r') as file:
        configuration = json.loads(file.read())
    return list(configuration['boards'].keys())


def create_boards(path: str):
    board_ips = get_board_ips_from_config(path)
    boards = {}
    for board_ip in board_ips:
        boards[board_ip] = PicoBoard(board_ip, 1234)

    return boards
