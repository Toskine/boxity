import time
import grovepi
from grove_rgb_lcd import *

# Définition des ports
dht_sensor_port = 7  # DHT sur D7
dht_sensor_type = 0  # Type 0 pour DHT11 (1 pour DHT22)

while True:
    try:
        [temperature, humidity] = grovepi.dht(dht_sensor_port, dht_sensor_type)

        # Protection si lecture échoue
        if temperature is None or humidity is None:
            print("Erreur de lecture capteur DHT")
            continue

        # Formatage
        t = str(round(temperature, 1))
        h = str(round(humidity, 1))
        print(f"Temp: {float(t):.2f}C  Humidity: {float(h):.2f}%")

        # Couleur verte pour afficher (R, G, B)
        setRGB(0,255 ,255)

        # Affichage sur 2 lignes
        setText_norefresh(f"Temp: {float(t):.2f}C\nHumidity: {float(h):.2f}%")



        time.sleep(2)

    except IOError:
        print("Erreur de lecture")
    except KeyboardInterrupt:
        setText("")
        setRGB(0, 0, 0)
        break 
