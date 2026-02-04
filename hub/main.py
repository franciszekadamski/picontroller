#!/usr/bin/python3


import time

from lh_controller import LHController


CONFIGURATION_FILE_PATH = 'configuration_files/configuration.json'


if __name__ == "__main__":
    controller = LHController(CONFIGURATION_FILE_PATH)
    controller.main_loop()
