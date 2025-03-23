import RPi.GPIO as GPIO
import time

button_pin = 15
led_pin = 4

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(led_pin, GPIO.OUT)

light_on = False
prev_input = 0

try:
    while True:
        input_state = GPIO.input(button_pin)
        if input_state == GPIO.HIGH and prev_input == GPIO.LOW:
            light_on = not light_on
            GPIO.output(led_pin, light_on)
            print("LED ON!" if light_on else "LED OFF!")
        prev_input = input_state
        time.sleep(0.05)
except KeyboardInterrupt:
    GPIO.cleanup()
