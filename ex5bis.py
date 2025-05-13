import time
import grovepi
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt
import json
import serial
import math
import mido
import os


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
LIGHT_THRESHOLD = 300  # Seuil de luminosité

NOTES = {
    'C4': 262,
    'E4': 330,
    'G4': 392,
    'C5': 523,
    'E5': 659,
    'G5': 784
}

# Dictionary to convert MIDI note numbers to frequencies (Hz)
MIDI_TO_FREQ = {}
for i in range(128):
    MIDI_TO_FREQ[i] = 440.0 * (2.0 ** ((i - 69) / 12.0))

def play_tone(note_or_freq, duration=0.2):
    # Determine if input is a note name or a frequency
    if isinstance(note_or_freq, str) and note_or_freq in NOTES:
        freq = NOTES[note_or_freq]
    else:
        freq = note_or_freq
        
    if freq <= 0:
        time.sleep(duration)
        return
        
    for _ in range(int(duration * 100)):  # Augmenté de 20 à 100 cycles
        grovepi.digitalWrite(BUZZER_PORT, 1)
        time.sleep(1.0 / (2 * freq))  # Demi-période
        grovepi.digitalWrite(BUZZER_PORT, 0)
        time.sleep(1.0 / (2 * freq))

def play_mario_tune():
    try:
        # Open Mario.mid file from the same directory as this script
        midi_file_path = 'Mario.mid'
        
        # Load and parse the MIDI file
        mid = mido.MidiFile(midi_file_path)
        print(f"MIDI: Chargement du fichier {midi_file_path} réussi")
        
        # Default tempo (microseconds per beat)
        tempo = 500000
        ticks_per_beat = mid.ticks_per_beat
        
        # Play notes from the MIDI file
        for msg in mid:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            
            if not isinstance(msg, mido.MetaMessage):
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Play the note
                    freq = MIDI_TO_FREQ[msg.note]
                    
                    # Convert time from MIDI ticks to seconds
                    # Simple approximation using a fixed duration
                    duration = 0.2
                    
                    print(f"MIDI: Note {msg.note} (freq={freq:.2f}Hz)")
                    play_tone(freq, duration)
                    
                    # Wait for the next message time
                    if msg.time > 0:
                        seconds = mido.tick2second(msg.time, ticks_per_beat, tempo)
                        time.sleep(max(0.01, seconds))  # Ensure at least a small delay
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Handle time for note off events
                    if msg.time > 0:
                        seconds = mido.tick2second(msg.time, ticks_per_beat, tempo)
                        time.sleep(max(0.01, seconds))
    except Exception as e:
        print(f"Erreur lecture MIDI: {e}")
        # Fallback to simple beep if MIDI fails
        buzz(0.2, 2)

def buzz(duration=0.4, count=1): 
    for _ in range(count):
        for _ in range(50):  # Répétition rapide pour plus de volume
            grovepi.digitalWrite(BUZZER_PORT, 1)
            time.sleep(0.001)
            grovepi.digitalWrite(BUZZER_PORT, 0)
            time.sleep(0.001)
        if count > 1:
            time.sleep(0.05)


try:
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
        setText("")  # Clear screen first
        setText(text)  # Then write new text
    except:
        print(f"[LCD] {text}")

print("Démarrage monitoring...")
mode = 0  # 0=Temp/Hum/GPS, 1=Light/GPS, 2=GPS/City
last_btn = 0

while True:
    try:
        # Gestion bouton et LED
        btn = grovepi.digitalRead(BTN_PORT)
        if btn and not last_btn:
            mode = (mode + 1) % 3  # Cycle entre 0, 1 et 2
            print("Mode:", ["Temp/Hum", "Light/GPS", "GPS/City"][mode])
            # Toggle LED on mode change (ON pour modes 1 et 2)
            grovepi.digitalWrite(LED_PORT, 1 if mode > 0 else 0)
            time.sleep(0.2)  # Anti-rebond
        last_btn = btn

        # Lecture capteurs
        light = grovepi.analogRead(LIGHT_PORT)
        # Vérification luminosité
        if light < LIGHT_THRESHOLD:
            print(f"Luminosité faible: {light} < {LIGHT_THRESHOLD}")
            play_mario_tune()

        lat, lon, alt = ("50.6278", "3.0583", "28.2")  # Corrigé format des coordonnées
    
        # Données MQTT
        mqtt_data = {
            "timestamp": time.time(),
            "light": light,
            "mode": mode,
            "gps": {
                "lat": lat,
                "lon": lon,
                "alt": alt
            }
        }

        # Affichage selon mode
        if mode == 0:  # Mode Temp/Hum
            temp, hum = grovepi.dht(DHT_PORT, 0)
            
            if not math.isnan(temp) and not math.isnan(hum):
                mqtt_data.update({"temp": temp, "humidity": hum})
                safe_display(
                    f"T:{temp:.1f}C\n"
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
grovepi.digitalWrite(LED_PORT, 0)  # Turn off LED
grovepi.digitalWrite(BUZZER_PORT, 0) 
setRGB(0,0,0)
setText("")
print("Terminé.")