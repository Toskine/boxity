import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
import serial
import math
import mido
import os
import smbus
from grove.i2c import Bus   # Import du baromètre

# Configuration MQTT
MQTT_BROKER = "10.34.164.21"
MQTT_PORT = 1883
MQTT_TOPIC = "boxity/capteurs"

# Configuration des ports
DHT_PORT = 7     # D7
LIGHT_PORT = 0   # A0
BTN_PORT = 6     # D6
LED_PORT = 4     # D4
BUZZER_PORT = 3  # D3
LIGHT_THRESHOLD = 300  # Seuil de luminosité

# Initialisation du baromètre
try:
    bus = Bus(3)  # I2C bus 3
    bmp = bus.sensor(0x77)  # Adresse I2C du BMP280
    print("Baromètre initialisé")
    baro_ok = True
except Exception as e:
    print(f"Erreur baromètre: {e}")
    baro_ok = False

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

NOTES = {
    'C4': 262,
    'E4': 330,
    'G4': 392,
    'C5': 523,
    'E5': 659,
    'G5': 784
}

def play_short_tune():
    """Joue une courte mélodie"""
    notes = ['E5', 'G5', 'C5']
    durations = [0.15, 0.15, 0.2]
    
    for note, duration in zip(notes, durations):
        play_tone(note, duration)
        time.sleep(0.05)

def play_tone(note_or_freq, duration=0.2):
    if isinstance(note_or_freq, str) and note_or_freq in NOTES:
        freq = NOTES[note_or_freq]
    else:
        freq = note_or_freq
        
    if freq <= 0:
        time.sleep(duration)
        return
        
    cycles = int(duration * freq)
    period = 1.0 / freq
    
    for _ in range(cycles):
        grovepi.digitalWrite(BUZZER_PORT, 1)
        time.sleep(period/2)
        grovepi.digitalWrite(BUZZER_PORT, 0)
        time.sleep(period/2)

def buzz(duration=0.1, count=3): 
    for _ in range(count):
        for _ in range(100):  # Plus de répétitions pour plus de volume
            grovepi.digitalWrite(BUZZER_PORT, 1)
            time.sleep(0.001)
            grovepi.digitalWrite(BUZZER_PORT, 0)
            time.sleep(0.001)
        if count > 1:
            time.sleep(0.05)

# Initialisation du matériel
try:
    grovepi.pinMode(BTN_PORT, "INPUT")
    grovepi.pinMode(LED_PORT, "OUTPUT")
    grovepi.pinMode(BUZZER_PORT, "OUTPUT")
    grovepi.digitalWrite(LED_PORT, 0)
    grovepi.digitalWrite(BUZZER_PORT, 0)
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
        setText("")  # Clear screen first
        setText(text)  # Then write new text
    except:
        print(f"[LCD] {text}")

print("Démarrage monitoring...")
mode = 0  # 0=Temp/Hum/Baro, 1=Light/GPS, 2=GPS/City
last_btn = 0

while True:
    try:
        # Gestion bouton et LED
        btn = grovepi.digitalRead(BTN_PORT)
        if btn and not last_btn:
            mode = (mode + 1) % 3
            print("Mode:", ["Temp/Hum/Baro", "Light/GPS", "GPS/City"][mode])
            grovepi.digitalWrite(LED_PORT, 1 if mode > 0 else 0)
            time.sleep(0.2)
        last_btn = btn

        # Lecture capteurs
        light = grovepi.analogRead(LIGHT_PORT)
        if baro_ok:
            pressure = bmp.readPressure() / 100.0  # Conversion en hPa
            baro_temp = bmp.readTemperature()
            altitude = bmp.readAltitude(101560)  # Altitude basée sur pression au niveau de la mer
        else:
            pressure = baro_temp = altitude = None

        # Vérification luminosité
        if light < LIGHT_THRESHOLD:
            print(f"Luminosité faible: {light} < {LIGHT_THRESHOLD}")
            play_short_tune()

        lat, lon, alt = ("50.6278", "3.0583", "28.2")
    
        # Données MQTT
        mqtt_data = {
            "timestamp": time.time(),
            "light": light,
            "mode": mode,
            "gps": {
                "lat": lat,
                "lon": lon,
                "alt": alt
            },
            "barometer": {
                "pressure": pressure,
                "temperature": baro_temp,
                "altitude": altitude
            }
        }


        # Affichage selon mode
        if mode == 0:  # Mode Temp/Hum/Baro
            temp, hum = grovepi.dht(DHT_PORT, 0)
            
            if not math.isnan(temp) and not math.isnan(hum):
                mqtt_data.update({"temp": temp, "humidity": hum})
                safe_display(
                    f"T:{temp:.1f}C {pressure:.0f}hPa\n" if pressure else f"T:{temp:.1f}C\n"
                    f"H:{hum:.1f}%"
                )
            else:
                safe_display("Err DHT", color=(255,0,0))
                
        elif mode == 1:  # Mode Light/GPS
            safe_display(
                f"L:{light}\n"
                f"GPS: {lat},{lon}"
            )
            
        else:  # Mode GPS/City (mode 2)
            safe_display(
                f"{lat},{lon}\n"
                f"Lille"
            )

        # Envoi MQTT
        client.publish(MQTT_TOPIC, json.dumps(mqtt_data))
        
        time.sleep(1)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Erreur: {e}")
        time.sleep(0.5)

# Nettoyage
print("\nArrêt...")
client.loop_stop()
client.disconnect()
grovepi.digitalWrite(LED_PORT, 0)
grovepi.digitalWrite(BUZZER_PORT, 0)
setRGB(0,0,0)
setText("")
print("Terminé.")