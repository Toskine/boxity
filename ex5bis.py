import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
import smbus2

# Configuration MQTT
MQTT_BROKER = "10.34.164.21"
MQTT_PORT = 1883
MQTT_TOPIC = "boxity/capteurs"

# Configuration I2C
bus = smbus2.SMBus(1)  # bus I2C numéro 1
AIR_QUALITY_ADDR = 0x04
BME280_ADDR = 0x77

# Registres BME280
BME280_TEMP_REG = 0xFA
BME280_PRESSURE_REG = 0xF7
BME280_HUMIDITY_REG = 0xFD
BME280_CTRL_HUM_REG = 0xF2
BME280_CTRL_MEAS_REG = 0xF4
BME280_CONFIG_REG = 0xF5

def init_bme280():
    # Configuration du BME280 pour plus de précision
    bus.write_byte_data(BME280_ADDR, BME280_CTRL_HUM_REG, 0x01)  # Humidité x1
    bus.write_byte_data(BME280_ADDR, BME280_CTRL_MEAS_REG, 0xB7)  # Temp x2, Pressure x16, Normal mode
    bus.write_byte_data(BME280_ADDR, BME280_CONFIG_REG, 0xB0)  # Standby 500ms, Filter x16

def read_bme280():
    try:
        data = bus.read_i2c_block_data(BME280_ADDR, BME280_TEMP_REG, 8)
        temp = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        pressure = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        humidity = (data[6] << 8) | data[7]
        
        # Conversion approximative
        temp = (temp / 100.0) - 40
        pressure = (pressure / 256.0) + 300
        humidity = (humidity / 1024.0) * 100
        
        return temp, pressure, humidity
    except Exception as e:
        print(f"Erreur lecture BME280: {e}")
        return 0, 0, 0

def read_air_quality():
    try:
        return bus.read_byte(AIR_QUALITY_ADDR)
    except Exception as e:
        print(f"Erreur lecture Air Quality: {e}")
        return 0

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

# Initialisation des capteurs
init_bme280()
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
        temp_baro, pressure, humidity_bme = read_bme280()
        air_quality_value = read_air_quality()
        
        # Préparer le message MQTT
        mqtt_data = {
            "timestamp": time.time(),
            "light": light,
            "pressure": pressure,
            "humidity_bme": humidity_bme,
            "air_quality": air_quality_value,
            "temperature_baro": temp_baro
        }

        # Mode d'affichage et lectures supplémentaires
        if mode == 0:
            # Mode tous capteurs
            [temp_dht, humidity] = grovepi.dht(dht_sensor_port, 0)

            if not (temp_dht != temp_dht or humidity != humidity):
                setText_norefresh(f"T:{temp_dht:.1f}C P:{pressure:.0f}\nAQ:{air_quality_value}")
                print(f"""
Mesures complètes:
- Température (DHT): {temp_dht:.1f}°C
- Humidité: {humidity:.1f}%
- Pression: {pressure:.0f}hPa
- Qualité air: {air_quality_value}
- Luminosité: {light}
- Température BME280: {temp_baro:.1f}°C
- Humidité BME280: {humidity_bme:.1f}%
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
        print(f"Erreur:", e)
        time.sleep(0.5)

# Nettoyage final
print("Fermeture des connexions...")
client.loop_stop()
client.disconnect()
setRGB(0,0,0)
setText("")
print("Programme terminé.")