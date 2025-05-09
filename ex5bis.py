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

# Configuration I2C pour Air Quality Sensor
AIR_QUALITY_ADDR = 0x04
BME280_ADDR = 0x77
bus = smbus2.SMBus(1)  # bus I2C numéro 1

# Configuration pour le BME280
# Registres BME280
BME280_REGISTER_DIG_T1 = 0x88
BME280_REGISTER_DIG_T2 = 0x8A
BME280_REGISTER_DIG_T3 = 0x8C
BME280_REGISTER_DIG_P1 = 0x8E
BME280_REGISTER_DIG_P2 = 0x90
BME280_REGISTER_DIG_P3 = 0x92
BME280_REGISTER_DIG_P4 = 0x94
BME280_REGISTER_DIG_P5 = 0x96
BME280_REGISTER_DIG_P6 = 0x98
BME280_REGISTER_DIG_P7 = 0x9A
BME280_REGISTER_DIG_P8 = 0x9C
BME280_REGISTER_DIG_P9 = 0x9E
BME280_REGISTER_DIG_H1 = 0xA1
BME280_REGISTER_DIG_H2 = 0xE1
BME280_REGISTER_DIG_H3 = 0xE3
BME280_REGISTER_DIG_H4 = 0xE4
BME280_REGISTER_DIG_H5 = 0xE5
BME280_REGISTER_DIG_H6 = 0xE7
BME280_REGISTER_CHIPID = 0xD0
BME280_REGISTER_RESET = 0xE0
BME280_REGISTER_CTRL_HUM = 0xF2
BME280_REGISTER_STATUS = 0xF3
BME280_REGISTER_CTRL_MEAS = 0xF4
BME280_REGISTER_CONFIG = 0xF5
BME280_REGISTER_PRESSUREDATA = 0xF7
BME280_REGISTER_TEMPDATA = 0xFA
BME280_REGISTER_HUMIDDATA = 0xFD

class BME280:
    def __init__(self, address=BME280_ADDR, bus_num=1):
        self.bus = smbus2.SMBus(bus_num)
        self.address = address
        self.calibration_params = {}
        self.initialize()
        
    def initialize(self):
        # Vérifier l'ID du capteur
        chip_id = self.bus.read_byte_data(self.address, BME280_REGISTER_CHIPID)
        if chip_id != 0x60:
            print(f"Erreur: BME280 non détecté, ID reçu: {chip_id}")
            return False
        
        # Lire les paramètres de calibration
        self.read_calibration_params()
        
        # Configuration du capteur
        # humidity oversampling x1
        self.bus.write_byte_data(self.address, BME280_REGISTER_CTRL_HUM, 0x01)
        # temperature oversampling x2, pressure oversampling x16, mode normal
        self.bus.write_byte_data(self.address, BME280_REGISTER_CTRL_MEAS, 0x57)
        # standby time 500ms, filter x16
        self.bus.write_byte_data(self.address, BME280_REGISTER_CONFIG, 0x94)
        
        time.sleep(0.5)  # Attendre que le capteur soit prêt
        return True
    
    def read_calibration_params(self):
        # Lire les coefficients de calibration
        # Pour la température
        self.calibration_params["dig_T1"] = self.read_word(BME280_REGISTER_DIG_T1)
        self.calibration_params["dig_T2"] = self.read_signed_word(BME280_REGISTER_DIG_T2)
        self.calibration_params["dig_T3"] = self.read_signed_word(BME280_REGISTER_DIG_T3)
        
        # Pour la pression
        self.calibration_params["dig_P1"] = self.read_word(BME280_REGISTER_DIG_P1)
        self.calibration_params["dig_P2"] = self.read_signed_word(BME280_REGISTER_DIG_P2)
        self.calibration_params["dig_P3"] = self.read_signed_word(BME280_REGISTER_DIG_P3)
        self.calibration_params["dig_P4"] = self.read_signed_word(BME280_REGISTER_DIG_P4)
        self.calibration_params["dig_P5"] = self.read_signed_word(BME280_REGISTER_DIG_P5)
        self.calibration_params["dig_P6"] = self.read_signed_word(BME280_REGISTER_DIG_P6)
        self.calibration_params["dig_P7"] = self.read_signed_word(BME280_REGISTER_DIG_P7)
        self.calibration_params["dig_P8"] = self.read_signed_word(BME280_REGISTER_DIG_P8)
        self.calibration_params["dig_P9"] = self.read_signed_word(BME280_REGISTER_DIG_P9)
        
        # Pour l'humidité
        self.calibration_params["dig_H1"] = self.bus.read_byte_data(self.address, BME280_REGISTER_DIG_H1)
        self.calibration_params["dig_H2"] = self.read_signed_word(BME280_REGISTER_DIG_H2)
        self.calibration_params["dig_H3"] = self.bus.read_byte_data(self.address, BME280_REGISTER_DIG_H3)
        
        h4 = self.bus.read_byte_data(self.address, BME280_REGISTER_DIG_H4)
        h4_1 = self.bus.read_byte_data(self.address, BME280_REGISTER_DIG_H4 + 1)
        h5 = self.bus.read_byte_data(self.address, BME280_REGISTER_DIG_H5 + 1)
        h5_1 = self.bus.read_byte_data(self.address, BME280_REGISTER_DIG_H5)
        
        self.calibration_params["dig_H4"] = (h4 << 4) | (h4_1 & 0x0F)
        self.calibration_params["dig_H5"] = (h5 << 4) | (h5_1 >> 4)
        self.calibration_params["dig_H6"] = self.bus.read_byte_data(self.address, BME280_REGISTER_DIG_H6)
        if self.calibration_params["dig_H6"] > 127:
            self.calibration_params["dig_H6"] -= 256
    
    def read_word(self, register):
        # Lire un mot de 16 bits (non signé)
        msb = self.bus.read_byte_data(self.address, register)
        lsb = self.bus.read_byte_data(self.address, register + 1)
        return (msb << 8) | lsb
    
    def read_signed_word(self, register):
        # Lire un mot de 16 bits (signé)
        value = self.read_word(register)
        if value > 32767:
            value -= 65536
        return value
    
    def get_raw_data(self):
        # Lire les données brutes des registres
        data = []
        for i in range(8):
            data.append(self.bus.read_byte_data(self.address, BME280_REGISTER_PRESSUREDATA + i))
        
        # Pression (20 bits)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        
        # Température (20 bits)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        
        # Humidité (16 bits)
        hum_raw = (data[6] << 8) | data[7]
        
        return temp_raw, pres_raw, hum_raw
    
    def read_temperature(self):
        # Lire et calculer la température en degrés Celsius
        temp_raw, _, _ = self.get_raw_data()
        var1 = ((temp_raw / 16384.0) - (self.calibration_params["dig_T1"] / 1024.0)) * self.calibration_params["dig_T2"]
        var2 = (((temp_raw / 131072.0) - (self.calibration_params["dig_T1"] / 8192.0)) * 
                ((temp_raw / 131072.0) - (self.calibration_params["dig_T1"] / 8192.0)) * 
                self.calibration_params["dig_T3"])
        t_fine = var1 + var2
        temperature = t_fine / 5120.0
        return temperature, t_fine
    
    def read_pressure(self):
        # Lire et calculer la pression en hPa
        _, pres_raw, _ = self.get_raw_data()
        temperature, t_fine = self.read_temperature()
        
        var1 = (t_fine / 2.0) - 64000.0
        var2 = var1 * var1 * self.calibration_params["dig_P6"] / 32768.0
        var2 = var2 + (var1 * self.calibration_params["dig_P5"] * 2.0)
        var2 = (var2 / 4.0) + (self.calibration_params["dig_P4"] * 65536.0)
        var1 = (self.calibration_params["dig_P3"] * var1 * var1 / 524288.0 + 
                self.calibration_params["dig_P2"] * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.calibration_params["dig_P1"]
        
        if var1 == 0:
            return 0
        
        pressure = 1048576.0 - pres_raw
        pressure = (pressure - (var2 / 4096.0)) * 6250.0 / var1
        var1 = self.calibration_params["dig_P9"] * pressure * pressure / 2147483648.0
        var2 = pressure * self.calibration_params["dig_P8"] / 32768.0
        pressure = pressure + (var1 + var2 + self.calibration_params["dig_P7"]) / 16.0
        
        # Convertir en hPa
        pressure = pressure / 100.0
        return pressure
    
    def read_humidity(self):
        # Lire et calculer l'humidité en %
        _, _, hum_raw = self.get_raw_data()
        temperature, t_fine = self.read_temperature()
        
        humidity = t_fine - 76800.0
        h4 = self.calibration_params["dig_H4"]
        h5 = self.calibration_params["dig_H5"]
        
        humidity = ((hum_raw - ((h4 * 64.0 + h5 / 16384.0) * humidity)) *
                   (self.calibration_params["dig_H2"] / 65536.0 *
                    (1.0 + self.calibration_params["dig_H6"] / 67108864.0 * humidity *
                     (1.0 + self.calibration_params["dig_H3"] / 67108864.0 * humidity))))
        
        humidity = humidity * (1.0 - self.calibration_params["dig_H1"] * humidity / 524288.0)
        
        if humidity > 100.0:
            humidity = 100.0
        elif humidity < 0.0:
            humidity = 0.0
            
        return humidity
    
    def read_altitude(self, sea_level_pressure=1013.25):
        # Calculer l'altitude à partir de la pression
        pressure = self.read_pressure()
        altitude = 44330.0 * (1.0 - pow(pressure / sea_level_pressure, (1.0/5.255)))
        return altitude

def read_air_quality():
    try:
        return bus.read_byte(AIR_QUALITY_ADDR)
    except:
        print("Erreur lecture Air Quality")
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
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # Version 2 de l'API de callback
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

# Initialisation du BME280
bme280 = BME280(address=BME280_ADDR)

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
        temp_baro = bme280.read_temperature()[0]
        pressure = bme280.read_pressure()
        altitude = bme280.read_altitude()
        humidity_bme = bme280.read_humidity()
        air_quality_value = read_air_quality()
        
        # Préparer le message MQTT de base
        mqtt_data = {
            "timestamp": time.time(),
            "light": light,
            "pressure": pressure,
            "altitude": altitude,
            "humidity_bme": humidity_bme,
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