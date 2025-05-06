import time
import grovepi
from grove_rgb_lcd import *

dht_sensor_port = 7     # D7
light_sensor_port = 0   # A0 (un port analogique)
button_port = 6         # D6

grovepi.pinMode(button_port, "INPUT")

setRGB(0, 255, 255)

mode = 0  # 0 = Temp/Hum, 1 = Lumière
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
                print("Mode changé:", mode)

        last_button_state = button_state

        # Lire capteur lumière
        light = grovepi.analogRead(light_sensor_port)

        # Lire DHT uniquement si en mode 0
        if mode == 0:
            [temp, humidity] = grovepi.dht(dht_sensor_port, 0)

            # Vérifier que la lecture est valide (pas nan)
            if not (temp != temp or humidity != humidity):  # test si NaN
                setText_norefresh(f"Temp:{temp:.1f}C\nHum:{humidity:.1f}%")
                print(f"Temp: {temp:.2f}C  Humidity: {humidity:.2f}%  Light: {light}")
            else:
                print(f"(Lecture DHT invalide) Light: {light}")
        else:
            setText_norefresh(f"Luminosity:\n{light}")
            print(f"Luminosity only mode. Light: {light}")
        time.sleep(1)

    except Exception as e:
        print("Erreur:", e)
        time.sleep(0.5)
