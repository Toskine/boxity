import grovepi

class LightSensor:
    def __init__(self, port: int):
        self.port = port

    def read(self) -> int:
        """
        Returns light level or None on error.
        """
        try:
            return grovepi.analogRead(self.port)
        except Exception as e:
            print(f"LightSensor error: {e}")
            return None