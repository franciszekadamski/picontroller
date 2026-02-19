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
        humidity_reading = self.send('humidity_sensor:read_humidity')
        temperature_reading = self.send('humidity_sensor:read_temperature')
        moisture_reading = self.send('moisture_sensor:read')

        try:
            humidity_p = float(humidity_reading.split(':')[1])
        except Exception as e:
            print(e)
            humidity_p = 300

        try:
            temperature_c = float(temperature_reading.split(':')[1])
        except Exception as e:
            print(e)
            temperature_c = 300

        try:
            moisture_raw = float(moisture_reading.split(':')[1])
        except Exception as e:
            print(e)
            moisture_raw = 300

        moisture_a = self.zmq_data_store['moisture_lr_a_factor']
        moisture_b = self.zmq_data_store['moisture_lr_b_factor']

        moisture_p = moisture_a * moisture_raw + moisture_b

        print(f"humidity: {humidity_p}")
        print(f"temperature: {temperature_c}")
        print(f"moisture: {moisture_p}")
        self.zmq_data_store['humidity'] = humidity_p
        self.zmq_data_store['temperature'] = temperature_c
        self.zmq_data_store['moisture'] = moisture_p

        self.zmq_data_store['humidity'] = humidity_p
        self.zmq_data_store['temperature'] = temperature_c
        self.zmq_data_store['moisture'] = moisture_p

        if humidity_p < self.zmq_data_store['humidity_watering_treshold_p']:
            return True
        elif moisture_p < self.zmq_data_store['moisture_watering_treshold_p']:
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
            int(self.zmq_data_store['lighting_start_time_h']),
            int(self.zmq_data_store['lighting_start_time_min'])
        )
        self.lighting_end_time = datetime.time(
            int(self.zmq_data_store['lighting_end_time_h']),
            int(self.zmq_data_store['lighting_end_time_min'])
        )
        now = time.monotonic()

        if now - self.last_watering_check_time >= self.zmq_data_store['watering_interval_s']:
            self.last_watering_check_time = now
            if self.is_dry():
                self.send('humidity_rotor:off')
            else:
                self.send('humidity_rotor:on')


        if self.is_light_time():
            answer = self.send('light_servo:down')
        else:
            answer = self.send('light_servo:up')

        if self.zmq_data_store['request']:
            answer = self.send(self.zmq_data_store['request'])
            self.zmq_data_store['request'] = ''
            time.sleep(0.5)

        self.send('builtin_led:blink')

