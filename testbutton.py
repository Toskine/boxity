import time
import grovepi

button = 6  # Change ce numéro selon ton branchement

grovepi.pinMode(button, "INPUT")

while True:
    state = grovepi.digitalRead(button)
    print("Button state:", state)
    time.sleep(0.5)
