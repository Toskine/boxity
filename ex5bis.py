import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json

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
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Erreur de connexion MQTT: {e}")

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

mode = 0  # 0 = Temp/Hum, 1 = Lumière
last_button_state = 0
last_toggle_time = 0

# Fonction pour afficher sur LCD de manière sécurisée
def safe_display(text):
    if lcd_ok:
        try:
            setText_norefresh(text)
        except:
            print(f"[LCD] {text}")  # Afficher dans console si écran non disponible
    else:
        print(f"[LCD] {text}")  # Afficher dans console si écran non disponible

while True:
    try:
        # Lecture bouton
        button_state = grovepi.digitalRead(button_port)

        if button_state == 1 and last_button_state == 0:
            current_time = time.time()
            if current_time - last_toggle_time > 0.5:
                mode = 1 - mode
                last_toggle_time = current_time
                print("Mode changé:", mode)

        last_button_state = button_state

        # Lire capteur lumière
        light = grovepi.analogRead(light_sensor_port)
        
        # Préparer le message MQTT
        mqtt_data = {
            "light": light,
            "mode": mode,
            "timestamp": time.time()
        }

        # Lire DHT uniquement si en mode 0
        if mode == 0:
            [temp, humidity] = grovepi.dht(dht_sensor_port, 0)

            # Vérifier que la lecture est valide (pas nan)
            if not (temp != temp or humidity != humidity):  # test si NaN
                safe_display(f"Temp:{temp:.1f}C\nHum:{humidity:.1f}%")
                print(f"Temp: {temp:.2f}C  Humidity: {humidity:.2f}%  Light: {light}")
                mqtt_data.update({
                    "temperature": temp,
                    "humidity": humidity
                })
            else:
                print(f"(Lecture DHT invalide) Light: {light}")
        else:
            safe_display(f"Luminosity:\n{light}")
            print(f"Luminosity only mode. Light: {light}")

        # Envoyer les données via MQTT
        try:
            client.publish(MQTT_TOPIC, json.dumps(mqtt_data))
        except Exception as e:
            print(f"Erreur d'envoi MQTT: {e}")

        time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt du programme...")
        break
    except Exception as e:
        print("Erreur:", e)
        time.sleep(0.5)

# Nettoyage à la fin du programme
client.loop_stop()
client.disconnect()
print("Programme terminé.")