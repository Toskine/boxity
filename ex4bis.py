import time
import grovepi

led  = 5  # Port D2
button = 6  # Port D1

grovepi.pinMode(led, "OUTPUT")
grovepi.pinMode(button, "INPUT")

while True:
    button_state = grovepi.digitalRead(button)

    if button_state == 1:
        print("LED ON")
        grovepi.digitalWrite(led, 1)
    else:
        print("LED OFF")
        grovepi.digitalWrite(led, 0)

        time.sleep(0.1)
