import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
from grove_bme280 import BME280
from grove_gas_sensor import GasSensor

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

def on_publish(client, userdata, mid):
    print(f"Message {mid} publié")

# Initialisation du client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

try:
    print(f"Connexion au broker MQTT {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Erreur de connexion MQTT: {e}")

print("Démarrage du programme de monitoring...")


# Initialisation des ports
dht_sensor_port = 7     # D7
light_sensor_port = 0   # A0 (un port analogique)
button_port = 6         # D6

# Initialisation des capteurs I2C
bme280 = BME280(0x77) #defaut du BMP180
air_quality = GasSensor(0x04)  # Air Quality Sensor

# Configuration des ports
grovepi.pinMode(button_port, "INPUT")
setRGB(0, 255, 255)

# Variables globales
mode = 0  # 0 = tous les capteurs, 1 = air quality et pression
last_button_state = 0
last_toggle_time = 0

while True:
    try:
        # Lecture bouton
        button_state = grovepi.digitalRead(button_port)

        if button_state == 1 and last_button_state == 0:
            current_time = time.time()
            if current_time - last_toggle_time > 0.5:
                mode = 1 - mode
                last_toggle_time = current_time
                print("Mode changé:", "Air Quality" if mode else "Tous capteurs")

        last_button_state = button_state

        # Lecture de tous les capteurs
        light = grovepi.analogRead(light_sensor_port)
        temp_baro = bme280.temperature  # Changement ici
        pressure = bme280.pressure / 100.0  # Conversion en hPa
        altitude = bme280.altitude
        humidity_bme = bme280.humidity  # Nouveau : le BME280 peut aussi mesurer l'humidité
        air_quality_value = air_quality.read()
        
        # Préparer le message MQTT de base
        mqtt_data = {
            "light": light,
            "mode": mode,
            "timestamp": time.time(),
            "pressure": pressure,
            "altitude": altitude,
            "humidity_bme": humidity_bme,  # Ajout de l'humidité du BME280
            "air_quality": air_quality_value,
            "temperature_baro": temp_baro
        }

        # Mode d'affichage et lectures supplémentaires
        if mode == 0:
            # Mode tous capteurs
            [temp_dht, humidity] = grovepi.dht(dht_sensor_port, 0)

            if not (temp_dht != temp_dht or humidity != humidity):  # Vérification NaN
                setText_norefresh(f"T:{temp_dht:.1f}C P:{pressure:.0f}\nAQ:{air_quality_value}")
                print(f"""
                            Mesures complètes:
                            - Température (DHT): {temp_dht:.1f}°C
                            - Humidité: {humidity:.1f}%
                            - Pression: {pressure:.0f}hPa
                            - Qualité air: {air_quality_value}
                            - Luminosité: {light}
                            - Altitude: {altitude:.1f}m
                            """)
                mqtt_data.update({
                    "temperature_dht": temp_dht,
                    "humidity": humidity
                })
            else:
                print("Erreur lecture DHT")
                setText_norefresh(f"Err DHT\nAQ:{air_quality_value}")
        else:
            # Mode air quality et pression
            setText_norefresh(f"AQ:{air_quality_value}\nP:{pressure:.0f}hPa")
            print(f"""
                Mesures air:
                - Qualité air: {air_quality_value}
                - Pression: {pressure:.0f}hPa
                - Température: {temp_baro:.1f}°C
                """)

        # Envoi des données via MQTT
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
print("Fermeture des connexions...")
client.loop_stop()
client.disconnect()
setRGB(0,0,0)
setText("")
print("Programme terminé.")