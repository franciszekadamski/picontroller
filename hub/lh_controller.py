import datetime
import json
import time


import basic_controller


class LHController(basic_controller.BasicController):
    def __init__(self, configuration_file_path: str):
        super().__init__(configuration_file_path)

        self.last_watering_check_time = time.monotonic()


    def is_dry(self):
        humidity_reading = self.send('humidity_sensor:read_humidity')
        temperature_reading = self.send('humidity_sensor:read_temperature')
        moisture_reading = self.send('moisture_sensor:read')

        def _parse_reading(reading: str, fallback: float, reading_name: str) -> float:
            try:
                return float(reading.split(':', 1)[1])
            except (AttributeError, IndexError, TypeError, ValueError) as e:
                self.logger.warning(f'Failed to parse {reading_name} reading "{reading}": {e}')
                return fallback

        humidity_p = _parse_reading(humidity_reading, 300.0, 'humidity')
        temperature_c = _parse_reading(temperature_reading, 300.0, 'temperature')
        moisture_raw = _parse_reading(moisture_reading, 300.0, 'moisture')

        moisture_a = self.zmq_data_store['moisture_lr_a_factor']
        moisture_b = self.zmq_data_store['moisture_lr_b_factor']

        moisture_p = moisture_a * moisture_raw + moisture_b

        self.logger.info(f'humidity: {humidity_p}')
        self.logger.info(f'temperature: {temperature_c}')
        self.logger.info(f'moisture: {moisture_p}')
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
                # answer = self.send('water_servo:swing')
                self.send('water_servo:up')
                time.sleep(0.5)
                self.send('water_servo:down')

        if self.is_light_time():
            answer = self.send('light_servo:down')
        else:
            answer = self.send('light_servo:up')

        if self.zmq_data_store['request']:
            answer = self.send(self.zmq_data_store['request'])
            self.zmq_data_store['request'] = ''
            time.sleep(0.5)

        self.send('builtin_led:blink')

