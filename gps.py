import os
import time
import serial
import requests

class GPS:
    XTRA_URL     = "https://xtra2.gpsonextra.net/xtra.bin"
    XTRA_FILE    = "/tmp/xtra.bin"
    XTRA_MAX_AGE = 6 * 3600   # 6 hours

    def __init__(self, port="/dev/ttyAMA0", baud=9600, fix_timeout=60):
        """
        Initialise le port série, charge l’A-GPS, et fait un warm-start.
        """
        try:
            print(f"↪️  Ouvrir {port}@{baud}")
            self.ser = serial.Serial(port, baud, timeout=1)
        except Exception as e:
            print(f"❌ Erreur ouverture port GPS: {e}")
            self.working = False
            return

        self.working = True
        self.last_position = None
        self.last_time = 0

        # 1) Télécharger & charger XTRA si besoin
        try:
            self._maybe_load_xtra()
        except Exception as e:
            print(f"⚠️ A-GPS échoué : {e}")

        # 2) Warm-start GPS
        print("⏳ Démarrage warm GPS…")
        self.ser.write(b'AT+CGPSPWR=1\r\n')  # power on GPS
        time.sleep(2)
        self.ser.flushInput()

        # 3) Attendre un fix rapide
        deadline = time.time() + fix_timeout
        while time.time() < deadline:
            self.ser.write(b'AT+CGPSSTATUS?\r\n')
            time.sleep(0.5)
            status = self.ser.readline().decode(errors='ignore').strip()
            print(f"AT+CGPSSTATUS? → {status}")
            if "2D Fix" in status or "3D Fix" in status:
                print("✅ Fix GPS acquis")
                break
            time.sleep(1)
        else:
            print(f"⚠️ Pas de fix en {fix_timeout}s, attendra ultérieurement")

    def _maybe_load_xtra(self):
        """Télécharge XTRA si fichier absent ou trop vieux, puis le pousse."""
        # Vérifier l’âge du fichier local
        age = None
        if os.path.exists(self.XTRA_FILE):
            age = time.time() - os.path.getmtime(self.XTRA_FILE)

        if age is None or age > self.XTRA_MAX_AGE:
            print("⬇️  Télécharger XTRA…")
            r = requests.get(self.XTRA_URL, timeout=10)
            r.raise_for_status()
            with open(self.XTRA_FILE, "wb") as f:
                f.write(r.content)
            print(f"💾 Enregistré {len(r.content)} bytes")

        data = open(self.XTRA_FILE, "rb").read()
        length = len(data)
        print(f"📤 Pousser XTRA ({length} bytes)…")
        # init upload
        self.ser.write(f'AT+CGPSXTRADATA={length}\r\n'.encode())
        time.sleep(0.5)
        prompt = self.ser.readline().decode(errors='ignore')
        if ">" not in prompt:
            raise RuntimeError(f"Pas de prompt '>' pour XTRA: {prompt!r}")
        # send blob
        self.ser.write(data)
        time.sleep(0.5)
        resp = self.ser.readline().decode(errors='ignore').strip()
        if "OK" not in resp:
            raise RuntimeError(f"Erreur XTRA push: {resp!r}")
        print("✔️ XTRA chargé")

    def decimal_degrees(self, raw):
        d = int(raw // 100)
        m = raw - d * 100
        return d + m/60

    def read_position(self):
        """
        Lit AT+CGPSINFO; si pas supporté, retombe sur NMEA $GPGGA.
        Retourne (lat, lon, alt) ou (None,None,None).
        """
        if not getattr(self, 'working', False):
            return None, None, None

        # Essayer l’interface AT+CGPSINFO
        self.ser.write(b'AT+CGPSINFO\r\n')
        time.sleep(0.5)
        line = self.ser.readline().decode(errors='ignore').strip()
        if line.startswith("+CGPSINFO:"):
            parts = line.split(":")[1].split(",")
            raw_lat, ns, raw_lon, ew = parts[0], parts[1], parts[2], parts[3]
            alt = None
            if len(parts) >= 7 and parts[6]:
                try:
                    alt = float(parts[6])
                except:
                    pass
            try:
                lat = self.decimal_degrees(float(raw_lat))
                lon = self.decimal_degrees(float(raw_lon))
                if ns == 'S': lat = -lat
                if ew == 'W': lon = -lon
            except:
                return None, None, None

            self.last_position = (lat, lon, alt)
            self.last_time = time.time()
            return lat, lon, alt

        # Sinon retomber sur NMEA GPGGA (bonus)
        for _ in range(3):
            chunk = self.ser.readline().decode('ascii', errors='ignore').strip()
            if chunk.startswith("$GPGGA"):
                parts = chunk.split(",")
                if parts[6] != '0':
                    lat = self.decimal_degrees(float(parts[2]))
                    lon = self.decimal_degrees(float(parts[4]))
                    if parts[3]=='S': lat=-lat
                    if parts[5]=='W': lon=-lon
                    try:
                        alt = float(parts[9])
                    except:
                        alt = None
                    self.last_position = (lat, lon, alt)
                    self.last_time = time.time()
                    return lat, lon, alt

        # Si on a une position récente (<10 s), la renvoyer
        if self.last_position and time.time() - self.last_time < 10:
            return self.last_position

        return None, None, None

    def close(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
