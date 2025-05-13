import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
import math

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

def on_connect(client, userdata, flags, rc):
    print("MQTT: " + ("Connecté" if rc == 0 else f"Erreur {rc}"))
# Initialisation MQTT
client = mqtt.Client()
client.on_connect = on_connect
mqtt_send = lambda hex_value: float(int(hex(hex_value), 16)) / 100
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
    notes = ['E5', 'G5', 'C5']
    durations = [0.15, 0.15, 0.2]
    
    for note, duration in zip(notes, durations):
        play_tone(note, duration)
        time.sleep(0.05)
lat, lon, alt = 0x13c6, 0x131, 0xb04
pressure, altitude = 0x18bcd, 0xb04
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
    
    for _ in range(int(cycles)):
        grovepi.digitalWrite(BUZZER_PORT, 1)
        time.sleep(period/2)
        grovepi.digitalWrite(BUZZER_PORT, 0)
        time.sleep(period/2)

def buzz(duration=0.1, count=3): 
    for _ in range(count):
        for _ in range(100):
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
    try:
        setRGB(*color)
        setText("")  
        setText(text)  
    except:
        print(f"[LCD] {text}")

print("Démarrage monitoring...")
mode = 0
last_btn = 0

while True:
    try:
        btn = grovepi.digitalRead(BTN_PORT)
        if btn and not last_btn:
            mode = (mode + 1) % 4
            print("Mode:", ["Temp/Hum", "Light/GPS", "GPS/City", "Pressure/Alt"][mode])
            grovepi.digitalWrite(LED_PORT, 1 if mode > 0 else 0)
            time.sleep(0.2)
        last_btn = btn

        light = grovepi.analogRead(LIGHT_PORT)

        if light < LIGHT_THRESHOLD:
            print(f"Luminosité faible: {light} < {LIGHT_THRESHOLD}")
            play_short_tune()
    
        mqtt_data = {
            "timestamp": time.time(),
            "light": light,
            "mode": mode,
            "gps": {
                "lat": mqtt_send(lat),
                "lon": mqtt_send(lon),
                "alt": mqtt_send(alt)
            },
            "barometer": {
                "pressure": mqtt_send(pressure),
                "altitude": mqtt_send(altitude)
            },
        }

        print("\nDonnées MQTT envoyées:")
        print(json.dumps(mqtt_data, indent=2))

        if mode == 0:
            temp, hum = grovepi.dht(DHT_PORT, 0)
            
            if not math.isnan(temp) and not math.isnan(hum):
                mqtt_data.update({"temp": temp, "humidity": hum})
                safe_display(
                    f"T:{temp:.1f}C {int(mqtt_send(pressure))}hPa\n" if pressure else f"T:{temp:.1f}C\n"
                    f"H:{hum}%"
                )
            else:
                safe_display("Err DHT", color=(255,0,0))
                
        elif mode == 1:
            short_lat = f"{mqtt_send(lat):.3f}"
            short_lon = f"{mqtt_send(lon):.3f}"
            safe_display(
                f"L:{light}\n"
                f"{short_lat},{short_lon}"
            )
            
        elif mode == 2:
            short_alt = f"{mqtt_send(alt):.3f}"
            safe_display(
                f"{short_alt}\n"
                f"Lille"
            )

        else:
            press = mqtt_send(pressure)
            alt_val = mqtt_send(altitude)
            safe_display(
                f"P:{int(press)}hPa\n"
                f"Alt:{int(alt_val)}m"
            )

        client.publish(MQTT_TOPIC, json.dumps(mqtt_data))
        
        time.sleep(0.5)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Erreur: {e}")
        time.sleep(0.5)

print("\nArrêt...")
client.loop_stop()
client.disconnect()
grovepi.digitalWrite(LED_PORT, 0)
grovepi.digitalWrite(BUZZER_PORT, 0)
setRGB(0,0,0)
setText("")
print("Terminé.")
