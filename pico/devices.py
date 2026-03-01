import machine
import time


class Device:
    def __init__(self, unknown_command_result: str = 'failed'):
        self._command_handlers = {}
        self._unknown_command_result = unknown_command_result

    @property
    def commands(self):
        return list(self._command_handlers.keys())

    def execute(self, command: str) -> str:
        handler = self._command_handlers.get(command)
        if handler is None:
            print(f'unknown command {command}')
            return self._unknown_command_result
        return handler()

    def __call__(self, command: str) -> str:
        return self.execute(command)

    def update_states(self) -> None:
        pass


class Sensor(Device):
    def __init__(self, device_specification: dict):
        super().__init__(unknown_command_result='failed')
        self.sensor = machine.ADC(device_specification['sensor_pin_number'])
        self.power = machine.Pin(device_specification['power_pin_number_3_3_v'], machine.Pin.OUT)
        self.a = device_specification['a']
        self.b = device_specification['b']
        self._command_handlers = {
            'read': self.read,
        }
        self.power_up()

    def equation(self, raw_value: int) -> float:
        return self.a * raw_value + self.b 

    def read(self) -> float | str:
        try:
            raw_value: int = self.sensor.read_u16()
            return self.equation(raw_value)
        except OSError as e:
            print(f'Error reading sensor: {e}')
            return 'failed'

    def power_down(self) -> None:
        self.power.value(0)

    def power_up(self) -> None:
        self.power.value(1)

    def set_a(self, value: float) -> None:
        self.a = value

    def set_b(self, value: float) -> None:
        self.b = value


class Servo(Device):
    def __init__(self, device_specification: dict):
        super().__init__(unknown_command_result='failed')
        self.servo = machine.PWM(machine.Pin(device_specification['pin_number']))
        self.up_angle_deg = device_specification['up_angle_deg']
        self.down_angle_deg = device_specification['down_angle_deg']
        self.min_ns = device_specification['min_ns']
        self.max_ns = device_specification['max_ns']
        self.servo.freq(device_specification['freq'])
        self._command_handlers = {
            'swing': self.swing,
            'up': self.up,
            'down': self.down,
        }
        self.swing_wait_time_s = device_specification['swing_wait_time_s']
        self.swing_start_time_s = time.time()
        self.current_swing_state = 'idle'
        self.down()

    def set_angle(self, angle: float) -> None:
        duty: int = int(self.min_ns + (self.max_ns - self.min_ns) * (angle / 180))
        self.servo.duty_u16(duty)

    def update_states(self) -> None:
        time_delta_s: float = time.time() - self.swing_start_time_s
        if self.current_swing_state == 'triggered':
            self.up()
            self.swing_start_time_s = time.time()
            self.current_swing_state = 'busy'
        elif self.current_swing_state == 'busy' and time_delta_s >= self.swing_wait_time_s:
            self.down()
            self.current_swing_state = 'idle'

    def up(self) -> str:
        self.current_swing_state = 'idle'
        self.set_angle(self.up_angle_deg)
        return 'is_up'

    def down(self) -> str:
        self.current_swing_state = 'idle'
        self.set_angle(self.down_angle_deg)
        return 'is_down'

    def swing(self) -> str:
        self.current_swing_state = 'triggered'
        return 'swinged'


class BuiltinLED(Device):
    def __init__(self, device_specification: dict):
        super().__init__(unknown_command_result='failed')
        self.led = machine.Pin('LED', machine.Pin.OUT)
        self.blink_up_time_s = device_specification['blink_up_time_s']
        self._command_handlers = {
            'blink': self.blink,
            'on': self.on,
            'off': self.off,
        }
        self.current_blink_state = 'idle'
        self.blink_start_time_s = time.time()

    def blink(self) -> str:
        self.led.on()
        self.current_blink_state = 'busy'
        self.blink_start_time_s = time.time()
        return 'blinked'

    def on(self) -> str:
        self.current_blink_state = 'idle'
        self.led.on()
        return 'is_on'

    def off(self) -> str:
        self.current_blink_state = 'idle'
        self.led.off()
        return 'is_off'

    def update_states(self) -> None:
        if self.current_blink_state == 'busy':
            time_delta_s: float = time.time() - self.blink_start_time_s
            if time_delta_s >= self.blink_up_time_s:
                self.led.off()
                self.current_blink_state = 'idle'
