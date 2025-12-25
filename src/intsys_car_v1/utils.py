import time

import gpiozero


def reset_mcu(factory, reset_pin=5):
    """
    Reset mcu on Robot Hat.

    This is helpful if the mcu somehow stuck in a I2C data
    transfer loop, and Raspberry Pi getting IOError while
    Reading ADC, manipulating PWM, etc.
    """
    mcu_reset = gpiozero.OutputDevice(reset_pin, pin_factory=factory)
    mcu_reset.off()
    time.sleep(0.01)
    mcu_reset.on()
    time.sleep(0.01)

    mcu_reset.close()
    time.sleep(0.2)