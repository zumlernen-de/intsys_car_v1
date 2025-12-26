import time

import gpiozero
from gpiozero.pins.lgpio import LGPIOFactory

from robot_hat.pwm import PWM

# Motor Left PWM P13
# Motor Left Dir Pin: D4 - 23
# Motor Right PWM P12
# Motor Right Dir Pin: D5 - 24

class Motor:
    """Motor"""
    PERIOD = 4095
    PRESCALER = 10
    DEFAULT_FREQ = 100  # Hz
    _is_reversed = False
    _is_in_reverse = False
    _speed = 0
    _min_speed_to_move = 0

    def __init__(self, pwm_pin, dir_pin, factory, min_speed_to_move=0, is_reversed=False, freq=DEFAULT_FREQ):
        """
        Initialize a motor

        :param pwm: Motor speed control pwm pin
        :type pwm: robot_hat.pwm.PWM
        :param dir: Motor direction control pin
        :type dir: robot_hat.pin.Pin
        """

        self.dir = gpiozero.OutputDevice(dir_pin, pin_factory=factory)
        self.freq = freq
        self._is_reversed = is_reversed
        self._min_speed_to_move = min_speed_to_move
        self.pwm = PWM(pwm_pin)
        self.pwm.period(4095)
        self.pwm.prescaler(10)
        self.pwm.freq(self.freq)
        self.pwm.pulse_width_percent(0)

        self._speed = 0

    @property
    def is_reversed(self):
        return self._is_in_reverse

    @is_reversed.setter
    def is_reversed(self, value):
        if self._is_reversed:
            value = not value
        if value:
            self.dir.on()
        else:
            self.dir.off()
        self._is_in_reverse = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        # Ensure speed to be between -100 and 100
        value = max(min(100, value), -100)

        self._speed = value
        scaled_speed = self._min_speed_to_move + (value / 100) * (100 - self._min_speed_to_move) if value != 0 else 0
        self.pwm.pulse_width_percent(abs(scaled_speed))
        self.is_reversed = value < 0

    def setSpeed(self, speed):
        self.speed = speed


def main():
    factory = LGPIOFactory()
    motor_left = Motor("P13", 23, factory, min_speed_to_move=25)
    motor_left.setSpeed(0)
    motor_right = Motor("P12", 24, factory, is_reversed=True, min_speed_to_move=25)
    motor_right.speed = 0
    while True:
        # Program needs to be running, if not the dir_pin is reset.
        time.sleep(1)



if __name__ == '__main__':
    main()
