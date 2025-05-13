import serial
import time

class GPSSensor:
    def __init__(self, port: str = "/dev/ttyAMA0", baud: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.last_position = None
        self.last_time = 0
        try:
            self.ser = serial.Serial(port, baud, timeout=timeout)
            self._wait_for_initial_fix()
            self.working = True
        except Exception as e:
            print(f"GPS init error: {e}")
            self.working = False

    def _wait_for_initial_fix(self, timeout: float = 10.0):
        """Wait until GPS has a fix or timeout expires."""
        start = time.time()
        while time.time() - start < timeout:
            lat, lon, alt = self.read_position(raw=True)
            if lat is not None:
                return
            time.sleep(0.5)
        print("GPS: no initial fix within timeout")

    def _parse_gpgga(self, line: str):
        parts = line.split(',')
        if len(parts) < 10 or parts[6] == '0':
            return None
        # convert ddmm.mmmm into decimal degrees
        def decdeg(raw, hemi):
            d = float(raw) // 100
            m = float(raw) % 100
            coord = d + m / 60
            if hemi in ['S', 'W']:
                coord = -coord
            return coord
        lat = decdeg(parts[2], parts[3])
        lon = decdeg(parts[4], parts[5])
        alt = float(parts[9])
        return lat, lon, alt

    def read_position(self, raw: bool = False) -> tuple:
        """
        Reads GPS until a GPGGA sentence with a fix is found or returns last valid position.
        If raw=True just parses first line.
        """
        if not getattr(self, 'working', False):
            return None, None, None
        try:
            for _ in range(10):
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$GPGGA'):
                    fix = self._parse_gpgga(line)
                    if fix:
                        self.last_position = fix
                        self.last_time = time.time()
                        return fix
            # fallback: return last known position if recent
            if self.last_position and (time.time() - self.last_time) < 10:
                return self.last_position
        except Exception as e:
            print(f"GPSSensor read error: {e}")
        return None, None, None

    def close(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()