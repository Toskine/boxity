import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
import serial
import pynmea2

# Configuration MQTT
MQTT_BROKER = "10.34.164.21"
MQTT_PORT = 1883
MQTT_TOPIC = "boxity/capteurs"

# Configuration GPS
try:
    gps = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
    print("GPS initialisé")
    gps_ok = True
except Exception as e:
    print(f"Erreur initialisation GPS: {e}")
    gps_ok = False

def read_gps():
    """Lit les données GPS et retourne lat, lon, alt si disponibles"""
    if not gps_ok:
        return None, None, None
    try:
        line = gps.readline().decode('ascii', errors='replace')
        if line.startswith('$GPGGA'):
            msg = pynmea2.parse(line)
            return msg.latitude, msg.longitude, msg.altitude
    except Exception as e:
        print(f"Erreur lecture GPS: {e}")
    return None, None, None

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
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Erreur de connexion MQTT: {e}")

# Configuration des ports
dht_sensor_port = 7     # D7
light_sensor_port = 0   # A0 (un port analogique)
button_port = 6         # D6

grovepi.pinMode(button_port, "INPUT")

# Initialisation de l'écran LCD avec gestion d'erreur
lcd_ok = True
try:
    setRGB(0, 255, 255)
    print("Écran LCD initialisé")
except OSError:
    lcd_ok = False
    print("Problème avec l'écran LCD - fonctionnant en mode sans écran")

mode = 0  # 0 = Temp/Hum/GPS, 1 = Lumière/GPS
last_button_state = 0
last_toggle_time = 0

# Fonction pour afficher sur LCD de manière sécurisée
def safe_display(text):
    if lcd_ok:
        try:
            setText_norefresh(text)
        except:
            print(f"[LCD] {text}")
    else:
        print(f"[LCD] {text}")

while True:
    try:
        # Lecture bouton
        button_state = grovepi.digitalRead(button_port)

        if button_state == 1 and last_button_state == 0:
            current_time = time.time()
            if current_time - last_toggle_time > 0.5:
                mode = 1 - mode
                last_toggle_time = current_time
                print("Mode changé:", "Lumière/GPS" if mode else "Temp/Hum/GPS")

        last_button_state = button_state

        # Lecture des capteurs
        light = grovepi.analogRead(light_sensor_port)
        lat, lon, alt = read_gps()
        
        # Préparer le message MQTT
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
        print(f"Erreur: {e}")
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