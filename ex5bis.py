import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
import serial
import math

from gps import GPS

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
DHT_PORT = 7     # D7
LIGHT_PORT = 0   # A0
BTN_PORT = 6     # D6
LED_PORT = 4     # D4
BUZZER_PORT = 3  # D3
LIGHT_THRESHOLD = 200

NOTES = {
    'C4': 262,
    'E4': 330,
    'G4': 392,
    'C5': 523,
    'E5': 659,
    'G5': 784
}

def play_tone(note, duration=0.2):
    """Joue une note sur le buzzer avec un volume BEAUCOUP plus fort"""
    for _ in range(int(duration * 100)):  # Augmenté de 20 à 100 cycles
        grovepi.digitalWrite(BUZZER_PORT, 1)
        time.sleep(1.0 / (2 * NOTES[note]))  # Demi-période
        grovepi.digitalWrite(BUZZER_PORT, 0)
        time.sleep(1.0 / (2 * NOTES[note]))

def play_mario_tune():
    """Joue le thème de Mario avec un volume BEAUCOUP plus fort"""
    notes = ['E5', 'G5', 'E5', 'C5', 'G4', 'C5']
    durations = [0.3, 0.3, 0.3, 0.3, 0.3, 0.6]  # Durées augmentées pour plus de volume
    
    for note, duration in zip(notes, durations):
        play_tone(note, duration)
        time.sleep(0.01)  # Délai très court entre les notes

def buzz(duration=0.4, count=1):  # Durée doublée
    """Fait bipper le buzzer beaucoup plus fort"""
    for _ in range(count):
        for _ in range(50):  # Répétition rapide pour plus de volume
            grovepi.digitalWrite(BUZZER_PORT, 1)
            time.sleep(0.001)
            grovepi.digitalWrite(BUZZER_PORT, 0)
            time.sleep(0.001)
        if count > 1:
            time.sleep(0.05)


try:
    gps = GPS()
    grovepi.pinMode(BTN_PORT, "INPUT")
    grovepi.pinMode(LED_PORT, "OUTPUT")  # Configure LED
    grovepi.digitalWrite(LED_PORT, 0)    # LED off initially
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
        # Gestion bouton et LED
        btn = grovepi.digitalRead(BTN_PORT)
        if btn and not last_btn:
            mode = 1 - mode
            print("Mode:", "Light/GPS" if mode else "Temp/Hum/GPS")
            # Toggle LED on mode change
            grovepi.digitalWrite(LED_PORT, mode)
        last_btn = btn

        # Lecture capteurs
        light = grovepi.analogRead(LIGHT_PORT)
        # Vérification luminosité
        if light < LIGHT_THRESHOLD:
            print(f"Luminosité faible: {light} < {LIGHT_THRESHOLD}")
            play_mario_tune()  # Joue la mélodie de Mario

           
        gps = GPS(fix_timeout=90)   # on peut étendre le timeout si le fix est long
        if not gps.working:
            print("GPS indisponible, arrêt ou fallback…")
        else:
            # au démarrage on peut forcer une première lecture
            lat, lon, alt = gps.read_position()
            if lat is None:
                print("Toujours pas de fix après init, en attente…")
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
                        f"T:{temp:.1f}C\n"
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
grovepi.digitalWrite(LED_PORT, 0)  # Turn off LED
grovepi.digitalWrite(BUZZER_PORT, 0) 
setRGB(0,0,0)
setText("")
print("Terminé.")