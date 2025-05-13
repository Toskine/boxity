import time
import serial

class GPS:
    def __init__(self, port="/dev/ttyAMA0", baud=9600, fix_timeout=60):
        """
        Initialise le port série et démarre le GPS du module SIM.
        Attends ensuite un fix GPS jusqu'à fix_timeout secondes.
        """
        try:
            print(f"Initialisation GPS sur {port} à {baud} bauds…")
            self.ser = serial.Serial(port, baud, timeout=1)
            self.working = True
        except Exception as e:
            print(f"Erreur GPS (ouverture port): {e}")
            self.working = False
            return

        # 1) Allumer le moteur GPS
        self.ser.write(b'AT+CGPSPWR=1\r\n')   # SIM808: power on GPS
        time.sleep(2)
        self.ser.flushInput()

        # 2) Réinitialisation froide (optionnel)
        self.ser.write(b'AT+CGPSRST=1\r\n')   # cold start
        time.sleep(2)
        self.ser.flushInput()

        # 3) Attendre le fix
        print("Attente du fix GPS…")
        deadline = time.time() + fix_timeout
        while time.time() < deadline:
            self.ser.write(b'AT+CGPSSTATUS?\r\n')
            time.sleep(1)
            status = self.ser.readline().decode('ascii', errors='ignore').strip()
            print(f"AT+CGPSSTATUS? → {status}")
            if "3D Fix" in status or "2D Fix" in status:
                print("→ Fix GPS acquis !")
                break
            time.sleep(2)
        else:
            print(f"⚠️ Pas de fix GPS en {fix_timeout}s.")
            # On peut choisir ici de désactiver self.working,
            # ou continuer et renvoyer None jusqu'à ce qu'il y ait un fix.
            # self.working = False

        # On garde en mémoire la dernière bonne position lue
        self.last_position = None
        self.last_time = 0

    def decimal_degrees(self, raw):
        """Convertit un float DDMM.MMMM en degrés décimaux."""
        d = int(raw // 100)
        m = raw - (d*100)
        return d + m/60

    def read_position(self):
        """
        Lit AT+CGPSINFO pour récupérer lat/lon/alt.
        Si ça échoue, renvoie (None, None, None).
        """
        if not getattr(self, 'working', False):
            return None, None, None

        # Demande les infos GPS
        self.ser.write(b'AT+CGPSINFO\r\n')
        time.sleep(1)
        line = self.ser.readline().decode('ascii', errors='ignore').strip()
        print(f"AT+CGPSINFO → {line}")

        # Exemple de réponse : +CGPSINFO: 4916.45,N,12311.12,W,080412.00,0.5,101.5
        if line.startswith("+CGPSINFO:"):
            parts = line.split(":")[1].split(",")
            # latitude raw, N/S, longitude raw, E/W, utc, speed, altitude, etc...
            raw_lat, ns, raw_lon, ew = parts[0], parts[1], parts[2], parts[3]
            alt = None
            if len(parts) >= 7 and parts[6]:
                try:
                    alt = float(parts[6])
                except:
                    pass

            try:
                lat = self.decimal_degrees(float(raw_lat))
                if ns == 'S':
                    lat = -lat
                lon = self.decimal_degrees(float(raw_lon))
                if ew == 'W':
                    lon = -lon
            except ValueError:
                return None, None, None

            self.last_position = (lat, lon, alt)
            self.last_time = time.time()
            print(f"Position GPS: {lat:.6f}, {lon:.6f}, alt={alt}")
            return lat, lon, alt

        # Pas de donnée GPS valide
        return None, None, None

    def close(self):
        """Ferme le port série."""
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()