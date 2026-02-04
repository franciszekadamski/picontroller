import machine
import time
import sys
import uasyncio


class Sensor:
    def __init__(self, device_specification: dict):
        self.sensor = machine.ADC(device_specification['sensor_pin_number'])
        self.power = machine.Pin(device_specification['power_pin_number_3_3_v'], machine.Pin.OUT)
        self.a = device_specification['a']
        self.b = device_specification['b']
        self.commands = ['read']
        self.power_up()


    def equation(self, raw_value):
        return self.a * raw_value + self.b 

    def read(self):
        try:
            raw_value = self.sensor.read_u16()
            return self.equation(raw_value)
        except OSError as e:
            print("Error: humidity could not be read")


    def power_down(self):
        self.power.value(0)


    def power_up(self):
        self.power.value(1)


    def set_a(self, value: float):
        self.a = value


    def set_b(self, value: float):
        self.b = value


    def __call__(self, command: str):
        if command not in self.commands:
            print(f'unknown command {command}')
            return 'FAILED'
        elif command == 'read':
            return self.read()


    def update_states(self):
        pass


class Servo:
    def __init__(self, device_specification: dict):
        self.servo = machine.PWM(machine.Pin(device_specification['pin_number']))
        self.up_angle_deg = device_specification['up_angle_deg']
        self.down_angle_deg = device_specification['down_angle_deg']
        self.min_ns = device_specification['min_ns']
        self.max_ns = device_specification['max_ns']
        self.servo.freq(device_specification['freq'])
        self.commands = [
            'swing',
            'up',
            'down'
        ]

        self.swing_wait_time_s = device_specification['swing_wait_time_s']
        self.swing_start_time_s = time.time()
        self.swing_states = ['idle', 'triggered', 'busy']
        self.current_swing_state = 'idle'

        self.down()


    def set_angle(self, angle):
        duty = int(self.min_ns + (self.max_ns - self.min_ns) * (angle / 180))
        self.servo.duty_u16(duty)


    def up(self):
        self.set_angle(self.up_angle_deg)


    def down(self):
        self.set_angle(self.down_angle_deg)


    def swing(self):
        self.current_swing_state = 'triggered'


    def update_states(self):
        time_delta_s = time.time() - self.swing_start_time_s
        if self.current_swing_state == 'triggered':
            self.up()
            self.swing_start_time_s = time.time()
            self.swing_state = 'busy'
        elif self.current_swing_state == 'busy' and time_delta_s >= self.swing_wait_time_s:
            self.down()
            self.current_swing_state = 'idle'


    def __call__(self, command: str):
        if command not in self.commands:
            print(f'unknown command {command}')
            return 'failed'
        elif command == 'swing':
            self.swing()
            return 'swinged'
        elif command == 'up':
            self.up()
            return 'is_up'
        elif command == 'down':
            self.down()
            return 'is_down'


class BuiltinLED:
    def __init__(self, device_specification: dict):
        self.led = machine.Pin('LED', machine.Pin.OUT)
        self.blink_up_time_s = device_specification['blink_up_time_s']
        self.commands = ['blink', 'on', 'off']


    def blink(self):
        self.led.on()
        time.sleep(self.blink_up_time_s)
        self.led.off()
        return 'blinked'


    def on(self):
        self.led.on()
        return 'is_on'


    def off(self):
        self.led.off()
        return 'is_off'


    def __call__(self, command:str):
        if command not in self.commands:
            print(f'unknown command {command}')
            return 'failed'
        elif command == 'blink':
            return self.blink()
        elif command == 'on':
            return self.on()
        elif command == 'off':
            return self.off()


    def update_states(self):
        pass
