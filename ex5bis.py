import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
import serial
import math

class GPS:
    def __init__(self, port="/dev/ttyAMA0", baud=9600):
        try:
            self.ser = serial.Serial(port, baud, timeout=0)
            self.ser.flush()
            print("GPS initialisé sur", port)
            self.working = True
        except Exception as e:
            print(f"Erreur initialisation GPS: {e}")
            self.working = False
        
        self.last_valid_position = None
        self.last_valid_time = 0

    def decimal_degrees(self, raw_degrees):
        try:
            degrees = float(raw_degrees) // 100
            d = float(raw_degrees) % 100 / 60
            return degrees + d
        except:
            return None

    def read_position(self):
        if not self.working:
            return None, None, None

        try:
            line = self.ser.readline().decode('ascii', errors='replace').strip()
            if line.startswith('$GPGGA'):
                parts = line.split(',')
                print(f"Trame GPS: {line}")  # Affichage de la trame brute
                
                if len(parts) >= 10 and parts[6] != '0':
                    try:
                        lat = self.decimal_degrees(float(parts[2]))
                        if parts[3] == 'S':
                            lat = -lat
                            
                        lon = self.decimal_degrees(float(parts[4]))
                        if parts[5] == 'W':
                            lon = -lon
                            
                        alt = float(parts[9])
                        
                        self.last_valid_position = (lat, lon, alt)
                        self.last_valid_time = time.time()
                        
                        print(f"Position GPS: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
                        return lat, lon, alt
                    except ValueError:
                        print("Erreur conversion données GPS")
                else:
                    sats = parts[7] if len(parts) > 7 else "?"
                    print(f"Attente fix GPS ({sats} satellites)")
                    
        except Exception as e:
            print(f"Erreur lecture GPS: {e}")
        
        if self.last_valid_position and time.time() - self.last_valid_time < 10:
            return self.last_valid_position
            
        return None, None, None

    def close(self):
        if self.working:
            self.ser.close()

# Configuration MQTT
MQTT_BROKER = "10.34.164.21"
MQTT_PORT = 1883
MQTT_TOPIC = "boxity/capteurs"

# Callbacks MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT")
    else:
        print(f"Échec de connexion au broker, code retour={rc}")

# Initialisation du client MQTT
client = mqtt.Client()
client.on_connect = on_connect

try:
    print(f"Connexion au broker MQTT {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Erreur de connexion MQTT: {e}")

# Configuration des ports
dht_sensor_port = 7     # D7
light_sensor_port = 0   # A0
button_port = 6         # D6

# Initialisation des capteurs
try:
    gps = GPS()
    gps_ok = gps.working
except Exception as e:
    print(f"Erreur création GPS: {e}")
    gps_ok = False

# Test des ports
try:
    grovepi.pinMode(button_port, "INPUT")
    print("Configuration des ports OK")
except Exception as e:
    print(f"Erreur configuration ports: {e}")
    exit(1)

# Initialisation de l'écran LCD
lcd_ok = True
try:
    setRGB(0, 255, 255)
    print("Écran LCD initialisé")
except Exception as e:
    lcd_ok = False
    print(f"Erreur LCD: {e}")
    print("Le programme continuera sans affichage LCD")

# Variables globales
mode = 0  # 0 = Temp/Hum/GPS, 1 = Lumière/GPS
last_button_state = 0
last_toggle_time = 0

def safe_display(text):
    if lcd_ok:
        try:
            setText_norefresh(text)
        except:
            print(f"[LCD] {text}")
    else:
        print(f"[LCD] {text}")

print("Démarrage du monitoring...")

while True:
    try:
        # Lecture bouton
        button_state = grovepi.digitalRead(button_port)

        if button_state == 1 and last_button_state == 0:
            current_time = time.time()
            if current_time - last_toggle_time > 0.5:
                mode = 1 - mode
                last_toggle_time = current_time
                print("Mode changé:", "Luminosité/GPS" if mode else "Temp/Hum/GPS")

        last_button_state = button_state

        # Lecture des capteurs
        light = grovepi.analogRead(light_sensor_port)
        lat, lon, alt = gps.read_position() if gps_ok else (None, None, None)
        
        # Préparer message MQTT
        mqtt_data = {
            "light": light,
            "mode": mode,
            "timestamp": time.time()
        }

        # Ajouter données GPS si disponibles
        if lat is not None:
            mqtt_data["gps"] = {
                "latitude": lat,
                "longitude": lon,
                "altitude": alt
            }

        # Mode d'affichage
        if mode == 0:
            [temp, humidity] = grovepi.dht(dht_sensor_port, 0)

            if not (temp != temp or humidity != humidity):
                if lat is not None:
                    safe_display(f"T:{temp:.1f}C GPS:{lat:.4f}\nH:{humidity:.1f}% {lon:.4f}")
                else:
                    safe_display(f"T:{temp:.1f}C No GPS\nH:{humidity:.1f}%")
                
                print(f"""
Mesures:
- Température: {temp:.1f}°C
- Humidité: {humidity:.1f}%
- Lumière: {light}
- GPS: {f"lat:{lat:.4f} lon:{lon:.4f} alt:{alt}m" if lat else "No Fix"}
""")
                mqtt_data.update({
                    "temperature": temp,
                    "humidity": humidity
                })
            else:
                safe_display("Err DHT\nGPS:" + ("OK" if lat else "No Fix"))
                print("Lecture DHT invalide")
        else:
            if lat is not None:
                safe_display(f"L:{light}\nGPS:{lat:.4f},{lon:.4f}")
            else:
                safe_display(f"L:{light}\nGPS: No Fix")
            
            print(f"""
Mesures:
- Lumière: {light}
- GPS: {f"lat:{lat:.4f} lon:{lon:.4f} alt:{alt}m" if lat else "No Fix"}
""")

        # Envoi MQTT
        try:
            client.publish(MQTT_TOPIC, json.dumps(mqtt_data))
        except Exception as e:
            print(f"Erreur d'envoi MQTT: {e}")

        time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt du programme...")
        break
    except Exception as e:
        print(f"Erreur:", e)
        time.sleep(0.5)

# Nettoyage final
print("Nettoyage...")
client.loop_stop()
client.disconnect()
if gps_ok:
    gps.close()
if lcd_ok:
    setRGB(0,0,0)
    setText("")
print("Programme terminé.")