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
                # Set a global timeout for the NEXT socket creation (the connection)
                socket.setdefaulttimeout(2.0)
                
                # Now create the Netcat object
                self.nc = nclib.Netcat((self.ip, self.port))
                
                # Set the timeout back to None (or your preferred default) 
                # so other parts of your Pi script aren't affected
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
            self.nc.send(f"{message}\n".encode())
            
            # This is the ONLY place nclib officially supports a timeout argument
            answer = self.nc.recv(timeout=1.0).decode().strip()
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
