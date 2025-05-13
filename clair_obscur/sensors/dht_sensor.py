import grovepi
import math

class DHTSensor:
    def __init__(self, port: int):
        self.port = port

    def read(self) -> tuple:
        """
        Returns a tuple (temperature, humidity) or (None, None) on error.
        """
        try:
            temp, hum = grovepi.dht(self.port, 0)
            if math.isnan(temp) or math.isnan(hum):
                return None, None
            return temp, hum
        except Exception as e:
            print(f"DHTSensor error: {e}")
            return None, None