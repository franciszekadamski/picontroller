import datetime
import json
import time

import zmq

from basic_controller import BasicController


class LHController(BasicController):
    def __init__(self, configuration_file_path: str):
        super().__init__(configuration_file_path)

        self.last_watering_check_time = time.monotonic()


    def is_dry(self):
        humidity_reading = self.send('humidity_sensor:read')
        moisture_reading = self.send('moisture_sensor:read')

        humidity_raw = float(humidity_reading.split(':')[1])
        moisture_raw = float(moisture_reading.split(':')[1])

        humidity_a = self.zmq_data_store['humidity_lr_a_factor']
        humidity_b = self.zmq_data_store['humidity_lr_b_factor']
        moisture_a = self.zmq_data_store['moisture_lr_a_factor']
        moisture_b = self.zmq_data_store['moisture_lr_b_factor']

        humidity = humidity_a * humidity_raw + humidity_b
        moisture = moisture_a * moisture_raw + moisture_b

        if humidity < self.zmq_data_store['humidity_watering_treshold_p']:
            return True
        elif moisture < self.zmq_data_store['moisture_watering_treshold_p']:
            return True
        else:
            return False


    def is_light_time(self):
        now = datetime.datetime.now().time()
        if self.lighting_start_time <= now < self.lighting_end_time:
            return True
        else:
            return False


    def main(self):
        self.lighting_start_time = datetime.time(
            self.zmq_data_store['lighting_start_time_h'],
            self.zmq_data_store['lighting_start_time_min']
        )
        self.lighting_end_time = datetime.time(
            self.zmq_data_store['lighting_end_time_h'],
            self.zmq_data_store['lighting_end_time_min']
        )
        now = time.monotonic()

        if now - self.last_watering_check_time >= self.zmq_data_store['watering_interval_s']:
            self.last_watering_check_time = now
            if self.is_dry():
                answer = self.send('water_servo:swing')

        if self.is_light_time():
            answer = self.send('light_servo:up')
        else:
            answer = self.send('light_servo:down')

        self.send('builtin_led:blink')

