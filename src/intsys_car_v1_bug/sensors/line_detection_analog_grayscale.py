from time import sleep
from smbus import SMBus

class AnalogGrayscale():
    def __init__(self, threshold=300, channel_left=0x17, channel_center = 0x16, channel_right=0x15):
        self.bus = SMBus(1)
        self.threshold = threshold

        self.greyscale_module_channels = {
            "left": channel_left,
            "center": channel_center,
            "right": channel_right,
        }

    def get_line_detection_value(self, address):
        # smbus only support 8 bit register address, so write 2 byte 0 first
        self.bus.write_word_data(0x14, address, 0)
        msb = self.bus.read_byte(0x14)
        lsb = self.bus.read_byte(0x14)
        value = (msb << 8) | lsb
        return value

    def get_line_detection_data(self):
        left = self.get_line_detection_value(self.greyscale_module_channels["left"])
        center = self.get_line_detection_value(self.greyscale_module_channels["center"])
        right = self.get_line_detection_value(self.greyscale_module_channels["right"])
        return dict(leftValue=left,
                    leftDetected=left < self.threshold,
                    centerValue=center,
                    centerDetected=center < self.threshold,
                    rightValue=right,
                    rightDetected=right < self.threshold,
                    )

def main():
    line_detection = AnalogGrayscale()
    loop(line_detection)

def loop(line_detection):
    while True:
        print(line_detection.get_line_detection_data())
        sleep(0.2)

if __name__ == '__main__':
    main()