import time
import grovepi

led = 4  # Port D4
grovepi.pinMode(led, "OUTPUT")

while True:
    print("LED ON")
    grovepi.digitalWrite(led, 1)
    time.sleep(1)

    print("LED OFF")
    grovepi.digitalWrite(led, 0)
    time.sleep(1)
