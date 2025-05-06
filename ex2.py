import time
import grovepi

led_red = 4   # Port D4
led_blue = 5  # Port D5

grovepi.pinMode(led_red, "OUTPUT")
grovepi.pinMode(led_blue, "OUTPUT")

while True:
    print("LED RED ON")
    grovepi.digitalWrite(led_red, 1)
    time.sleep(1)
    grovepi.digitalWrite(led_red, 0)

    print("LED BLUE ON")
    grovepi.digitalWrite(led_blue, 1)
    time.sleep(1)
    grovepi.digitalWrite(led_blue, 0)
