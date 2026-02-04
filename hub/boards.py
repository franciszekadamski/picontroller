#!/usr/bin/python3

import nclib
import json


class PicoBoard:
    def __init__(self, board_ip: str, board_port: int):
        self.ip = board_ip
        self.port = board_port


    def send(self, message: str):
        nc = nclib.Netcat((self.ip, self.port))
        nc.send(message.encode())
        try:
            answer = nc.recv(timeout=5).decode()
        except:
            print(f'timeout. answer: {answer}')
        nc.close()
        return answer


def read_board_ips(path: str):
    with open(path, 'r') as file:
        configuration = json.loads(file.read())
    return list(configuration['boards'].keys())


def create_boards(path: str):
    board_ips = read_board_ips(path)
    boards = {}
    for board_ip in board_ips:
        boards[board_ip] = PicoBoard(board_ip, 1234)

    return boards
