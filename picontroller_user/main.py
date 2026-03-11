#!/usr/bin/python3


import datetime
import json
import os
import sys
import time

import zmq

picontroller_hub_user = os.environ['PICONTROLLER_HUB_USER']
sys.path.insert(0, f'/home/{picontroller_hub_user}/picontroller/hub')

from basic_controller import BasicController


if __name__ == "__main__":
    controller = BasicController(os.environ['PICONTROLLER_CONFIGURATION_PATH'])
    controller.main_loop()

