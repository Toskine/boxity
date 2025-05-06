import time
import grovepi

led = 5        # Port D5
potentiometer = 2  # Port A2

grovepi.pinMode(led, "OUTPUT")

while True:
    value = grovepi.analogRead(potentiometer)
    print("Potentiometer value:", value)

    # Convert 0-1023 to 0-255
    brightness = int(value / 4)
    grovepi.analogWrite(led, brightness)
    time.sleep(0.1)
