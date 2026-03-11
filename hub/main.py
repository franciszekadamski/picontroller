#!/usr/bin/python3


import os
import time

from lh_controller import LHController


CONFIGURATION_FILE_PATH = os.environ['PICONTROLLER_CONFIGURATION_PATH']


if __name__ == "__main__":
    controller = LHController(CONFIGURATION_FILE_PATH)
    controller.main_loop()
