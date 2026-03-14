#!/usr/bin/python3


import datetime
import json
import os
import sys
import time

import zmq

sys.path.insert(0, f'{os.environ["PICONTROLLER_PROJECT_PATH"]}/hub')

from basic_controller import BasicController


if __name__ == "__main__":
    controller = BasicController(f"{os.environ['PICONTROLLER_CONFIGURATION_PATH']}/configuration.json")
    controller.main_loop()

