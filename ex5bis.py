import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json

# Configuration MQTT
MQTT_BROKER = "10.34.164.21"  # Adresse IP de votre broker
MQTT_PORT = 1883
MQTT_TOPIC = "boxity/capteurs"

# Callbacks MQTT pour le debug
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT")
    else:
        print(f"Échec de connexion au broker, code retour={rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} publié avec succès")

# Initialisation du client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

try:
    print(f"Tentative de connexion à {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Erreur de connexion MQTT: {e}")

# ...existing code...

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
                setText_norefresh(f"Temp:{temp:.1f}C\nHum:{humidity:.1f}%")
                print(f"Temp: {temp:.2f}C  Humidity: {humidity:.2f}%  Light: {light}")
                mqtt_data.update({
                    "temperature": temp,
                    "humidity": humidity
                })
            else:
                print(f"(Lecture DHT invalide) Light: {light}")
        else:
            setText_norefresh(f"Luminosity:\n{light}")
            print(f"Luminosity only mode. Light: {light}")

        # Envoyer les données via MQTT
        try:
            client.publish(MQTT_TOPIC, json.dumps(mqtt_data))
        except Exception as e:
            print(f"Erreur d'envoi MQTT: {e}")

        time.sleep(1)

    except Exception as e:
        print("Erreur:", e)
        time.sleep(0.5)

# Nettoyage à la fin du programme
client.loop_stop()
client.disconnect()