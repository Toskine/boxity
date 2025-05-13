import time
import math
from grove_rgb_lcd import setRGB, setText_norefresh
import grovepi

from sensors import DHTSensor, LightSensor, GPSSensor
from mqtt import MQTTClient

# Configuration
DHT_PORT = 7
LIGHT_PORT = 0
BTN_PORT = 6

MQTT_BROKER = "10.34.164.21"
MQTT_PORT = 1883
MQTT_TOPIC = "boxity/capteurs"

# Initialize sensors
sensors = {
    'dht': DHTSensor(DHT_PORT),
    'light': LightSensor(LIGHT_PORT),
    'gps': GPSSensor()
}

def safe_display(text: str, color: tuple = (0, 255, 255)):
    try:
        setRGB(*color)
        setText_norefresh(text)
    except:
        print(f"LCD: {text}")

# Initialize MQTT
mqttc = MQTTClient(MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
mqttc.connect()

print("Starting monitoring...")
mode = 0
last_btn = 0

try:
    while True:
        # Button toggle
        btn = grovepi.digitalRead(BTN_PORT)
        if btn and not last_btn:
            mode ^= 1
            print(f"Mode: {'Light/GPS' if mode else 'Temp/Hum/GPS'}")
        last_btn = btn

        # Read sensors
        light = sensors['light'].read()
        lat, lon, alt = sensors['gps'].read_position()

        data = {
            'timestamp': time.time(),
            'light': light,
            'mode': mode
        }
        if lat is not None:
            data['gps'] = {'lat': lat, 'lon': lon, 'alt': alt}

        if mode == 0:
            temp, hum = sensors['dht'].read()
            if temp is not None:
                data.update({'temp': temp, 'humidity': hum})
                if lat is not None:
                    safe_display(f"T:{temp:.1f}C {lat:.4f}\nH:{hum:.1f}% {lon:.4f}")
                else:
                    safe_display(f"T:{temp:.1f}C No GPS\nH:{hum:.1f}%")
            else:
                safe_display("Err DHT", (255, 0, 0))
        else:
            if lat is not None:
                safe_display(f"L:{light}\nGPS:{lat:.4f},{lon:.4f}")
            else:
                safe_display(f"L:{light}\nGPS: No Fix")

        mqttc.publish(data)
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    sensors['gps'].close()
    mqttc.disconnect()
    setRGB(0, 0, 0)
    setText_norefresh("")
    print("Terminated.")