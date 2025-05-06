import time
import grovepi

buzzer = 2  # Port D2
button = 6  # Port D4

grovepi.pinMode(buzzer, "OUTPUT")
grovepi.pinMode(button, "INPUT")

while True:
    button_state = grovepi.digitalRead(button)

    if button_state == 1:
        print("Buzzing")
        grovepi.digitalWrite(buzzer, 1)
    else:
        print("OFF")
        grovepi.digitalWrite(buzzer, 0)

        time.sleep(0.1)
