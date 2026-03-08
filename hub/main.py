#!/usr/bin/python3


import time

import lh_controller


CONFIGURATION_FILE_PATH = 'configuration_files/configuration.json'


if __name__ == "__main__":
    controller = lh_controller.LHController(CONFIGURATION_FILE_PATH)
    controller.main_loop()
