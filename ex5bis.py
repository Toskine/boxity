import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
import serial

class GPS:
    def __init__(self, port="/dev/ttyAMA0", baud=9600):
        try:
            print(f"Initialisation GPS sur {port} à {baud} bauds...")
            self.ser = serial.Serial(port, baud, timeout=1)
            self.ser.flush()
            
            print("Test réception GPS...")
            for i in range(10):  # Plus de tentatives
                line = self.ser.readline().decode('ascii', errors='replace').strip()
                if line:
                    print(f"Trame reçue: {line}")
                    self.working = True
                    break
                print(f"Attente données... ({i+1}/10)")
                time.sleep(0.5)
            
            if not line:
                raise Exception("Aucune donnée GPS")
                
        except Exception as e:
            print(f"Erreur GPS: {e}")
            self.working = False
        
        self.last_position = None
        self.last_time = 0

    def decimal_degrees(self, raw_degrees):
        try:
            degrees = float(raw_degrees) // 100
            minutes = float(raw_degrees) % 100
            return degrees + (minutes / 60)
        except:
            return None

    def read_position(self):
        if not self.working:
            return None, None, None

        try:
            for _ in range(5):  # Plus de tentatives
                line = self.ser.readline().decode('ascii', errors='replace').strip()
                print(f"Trame brute: {line}")  # Debug
                
                if line.startswith('$GPGGA'):
                    parts = line.split(',')
                    print(f"Fix: {parts[6]}, Satellites: {parts[7]}")
                    
                    if len(parts) >= 10 and parts[6] != '0':
                        try:
                            lat = self.decimal_degrees(float(parts[2]))
                            if parts[3] == 'S':
                                lat = -lat
                                
                            lon = self.decimal_degrees(float(parts[4]))
                            if parts[5] == 'W':
                                lon = -lon
                                
                            alt = float(parts[9])
                            
                            self.last_position = (lat, lon, alt)
                            self.last_time = time.time()
                            
                            print(f"Position: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
                            return lat, lon, alt
                            
                        except ValueError as e:
                            print(f"Erreur conversion: {e}")
                    else:
                        print(f"Pas de fix ({parts[7]} satellites)")
                        
        except Exception as e:
            print(f"Erreur lecture GPS: {e}")
        
        # Utiliser dernière position valide si récente
        if self.last_position and time.time() - self.last_time < 10:
            return self.last_position
            
        return None, None, None

    def close(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()

# Configuration MQTT
MQTT_BROKER = "10.34.164.21"
MQTT_PORT = 1883
MQTT_TOPIC = "boxity/capteurs"

def on_connect(client, userdata, flags, rc):
    print("MQTT: " + ("Connecté" if rc == 0 else f"Erreur {rc}"))

# Initialisation MQTT
client = mqtt.Client()
client.on_connect = on_connect

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Erreur MQTT: {e}")

# Configuration des ports
DHT_PORT = 7    # D7
LIGHT_PORT = 0  # A0
BTN_PORT = 6    # D6

# Initialisation matériel
try:
    gps = GPS()
    grovepi.pinMode(BTN_PORT, "INPUT")
    setRGB(0, 255, 255)
    print("Initialisation matériel OK")
    hardware_ok = True
except Exception as e:
    print(f"Erreur initialisation: {e}")
    hardware_ok = False

def safe_display(text, color=(0,255,255)):
    """Affichage sécurisé sur LCD"""
    try:
        setRGB(*color)
        setText_norefresh(text)
    except:
        print(f"[LCD] {text}")

print("Démarrage monitoring...")
mode = 0  # 0=Temp/Hum/GPS, 1=Light/GPS
last_btn = 0

while True:
    try:
        # Gestion bouton
        btn = grovepi.digitalRead(BTN_PORT)
        if btn and not last_btn:
            mode = 1 - mode
            print("Mode:", "Light/GPS" if mode else "Temp/Hum/GPS")
        last_btn = btn

        # Lecture capteurs
        light = grovepi.analogRead(LIGHT_PORT)
        lat, lon, alt = gps.read_position() if gps.working else (None, None, None)
        
        # Données MQTT
        mqtt_data = {
            "timestamp": time.time(),
            "light": light,
            "mode": mode
        }

        if lat is not None:
            mqtt_data["gps"] = {
                "lat": lat,
                "lon": lon,
                "alt": alt
            }

        # Affichage selon mode
        if mode == 0:
            temp, hum = grovepi.dht(DHT_PORT, 0)
            
            if not math.isnan(temp) and not math.isnan(hum):
                mqtt_data.update({"temp": temp, "humidity": hum})
                
                if lat is not None:
                    safe_display(
                        f"T:{temp:.1f}C {lat:.4f}\n"
                        f"H:{hum:.1f}% {lon:.4f}"
                    )
                else:
                    safe_display(
                        f"T:{temp:.1f}C No GPS\n"
                        f"H:{hum:.1f}%"
                    )
            else:
                safe_display("Err DHT", color=(255,0,0))
        else:
            if lat is not None:
                safe_display(
                    f"L:{light}\n"
                    f"GPS:{lat:.4f},{lon:.4f}"
                )
            else:
                safe_display(
                    f"L:{light}\n"
                    f"GPS: No Fix"
                )

        # Envoi MQTT
        client.publish(MQTT_TOPIC, json.dumps(mqtt_data))
        
        time.sleep(1)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Erreur: {e}")
        time.sleep(1)

# Nettoyage
print("\nArrêt...")
client.loop_stop()
client.disconnect()
gps.close()
setRGB(0,0,0)
setText("")
print("Terminé.")