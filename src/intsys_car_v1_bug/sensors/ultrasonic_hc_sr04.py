#Bibliotheken einbinden
import gpiozero
import time

from gpiozero.pins.lgpio import LGPIOFactory

def get_speed_of_sound(temperature_celsius):
    """
    Gibt die Schallgeschwindigkeit zurück. Die Schallgeschwindigkeit ist temperaturabhängig (je heißer, desto schneller).
    Diese Funktion nutzt die lineare Näherungsformel c_Luft = (331,5 + 0,6v)m/s, wobei v die Temperatur ist und c die
    Schallgeschwindigkeit in der Luft.
    :param temperature: Temperatur in Grad Celsius
    :return: Die Schallgeschwindigkeit in der Luft bei der angegebenen Temperatur
    """
    return 331.5 + 0.6 * temperature_celsius


class HC_SR04():
    def __init__(self, trigger_pin = 27, echo_pin = 22, factory = LGPIOFactory(), speed_of_sound = get_speed_of_sound(20)):
        self.trigger = gpiozero.OutputDevice(trigger_pin, pin_factory=factory)
        self.echo = gpiozero.InputDevice(echo_pin, pin_factory=factory)
        self.speed_of_sound = speed_of_sound

    def get_time_of_emit(self, echo):
        """
        Gibt den Zeitpunkt an, an dem die Töne ausgegeben werden. Ab diesem Zeitpunkt wird der ECHO Pin auf Aktiv geschaltet,
        das heißt wir warten darauf.
        :param request: Die angeforderten Verbindungen, für diese Funktion wird aber nur der ECHO Pin benötigt.
        :return: Zeitpunkt an dem der erste Ton ausgegeben wird.
        :exception: SystemError, wenn der ECHO Pin nicht auf aktiv geschalten wird, ist irgendein Fehler beim Abenden des
        Tons aufgetreten.
        """
        start_time = None
        echo_count = 0
        while echo.value == 0:
            if echo_count < 10000:
                start_time = time.time()
                echo_count += 1
            else:
                return None
                raise SystemError("Echo pulse not received")
        return start_time

    def get_time_echo_ends(self, echo):
        """
        Gibt den Zeitpunkt an, zu dem der Sensor die reflektierten Töne (8) empfangen hat. Wenn der Sensor innerhalb von
        38ms nicht alle Töne empfangen hat, geht er automatisch auf INAKTIVE. Das wäre ein Fehlerfall (bsp. Kein Objekt in
        Reichweite).
        :param request: Die angeforderten Verbindungen, für diese Funktion wird aber nur der ECHO Pin benötigt.
        :return: Zeitpunkt, an dem alle Töne empfangen wurden.
        """
        end_time = None
        while echo.value == 1:
            end_time = time.time()
        return end_time

    def emit_sound(self, trigger):
        """
        Gibt 8 kurze, hochfrequenten (40 kHz) Töne aus. Der Ausstoß wird eingeleitet, indem der Triggerpin für
        10µs (Mikrosekunden) auf ACTIVE geschalten wird.
        :param request: Die angeforderten Verbindungen, für diese Funktion wird aber nur der TRIGGER benötigt.
        :return: nichts
        """
        trigger.off()
        time.sleep(0.001)  # Warte 2 Mikrosekunden
        trigger.on()
        time.sleep(0.00001)  # Warte 10 Mikrosekunden
        trigger.off()

    def get_signal_time(self):
        """
        Berechnet die Distanz zum Objekt anhand der Zeit von der Ausgabe eines Tons bis zum vollständigen Empfang des
        reflektierten Tons. Anhand der Schallgeschwindigkeit kann aus diesem Zeitraum die Entfernung abgeleitet werden.
        :param request: Die angeforderten Verbindungen. TRIGGER & ECHO Pin werden benötigt.
        :param speed_of_sound: Schallgewindigkeit in m/s.
        :return: Die errechnete Distanz zum Objekt in cm.
        """
        self.emit_sound(self.trigger)
        signal_start = self.get_time_of_emit(self.echo)
        if not signal_start:
            return dict()
        signal_end = self.get_time_echo_ends(self.echo)
        time_passed_sec = signal_end - signal_start
        time_per_distance_sec = time_passed_sec / 2
        return time_per_distance_sec

    def get_data(self):
        time_per_distance_sec = self.get_signal_time()
        distance_m = time_per_distance_sec * self.speed_of_sound  # Durch 2 Teilen weil die Zeit hin + zurück gemessen wurde.
        distance_cm = distance_m * 100
        return dict(distance_m=distance_m,
                    distance_cm=distance_cm,
                    time_per_distance_sec=time_per_distance_sec,
                    speed_of_sound=self.speed_of_sound)

    def get_distance_cm(self):
        time_per_distance_sec = self.get_signal_time()
        distance_m = time_per_distance_sec * self.speed_of_sound  # Durch 2 Teilen weil die Zeit hin + zurück gemessen wurde.
        return distance_m * 100


def main():
    factory = LGPIOFactory()
    ultrasonic = HC_SR04(27, 22, get_speed_of_sound(20))
    GPIO_TRIGGER = 27
    GPIO_ECHO = 22

    loop(ultrasonic)

def loop(ultrasonic):
    while True:
        print("---- Neue Messung")
        result = ultrasonic.get_ultrasonic_data()
        if result["distance_cm"] == 0:
            print("Fehler in der Messung")
        # print(f"Dauer 1-Strecke in Mikrosekunden: {dauer:.15f}µs")
        print(f"Dauer 1-Strecke in Sekunden: {result['time_per_distance_sec']}s")
        print(f"Schallgeschwindigkeit: {result['speed_of_sound']}s")
        print(f"Distanz: {result['distance_cm']} cm")
        time.sleep(1)

if __name__ == '__main__':
    main()



