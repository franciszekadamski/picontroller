#!/usr/bin/python3

import nclib
import json
import socket


class PicoBoard:
    def __init__(self, board_ip: str, board_port: int):
        self.ip = board_ip
        self.port = board_port
        self.nc = None 

    def _connect(self):
        if self.nc is None:
            try:
                socket.setdefaulttimeout(2.0)
                self.nc = nclib.Netcat((self.ip, self.port))
                socket.setdefaulttimeout(None)
                return True
            except Exception as e:
                print(f"Connection failed to {self.ip}: {e}")
                self.nc = None
                return False
        return True

    def send(self, message: str):
        if not self._connect():
            return "Error: No Connection"
        try:
            while True:
                try:
                    junk = self.nc.recv(timeout=0.01)
                    if not junk:
                        break
                except:
                    break
            self.nc.send(f"{message}\n".encode())
            answer = self.nc.recv(timeout=1.0).decode().strip() 
            if '\n' in answer:
                answer = answer.split('\n')[:-1].strip()
            return answer
        except Exception as e:
            print(f"Socket error on {self.ip}: {e}")
            if self.nc:
                self.nc.close()
            self.nc = None
            return "Error: Connection Lost"


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
