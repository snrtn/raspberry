import RPi.GPIO as GPIO
import time

led_pins = [5, 6, 13]
button_pins = [16, 20, 21]

led_states = [False, False, False]
prev_button_states = [False, False, False]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

for pin in button_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        for i in range(3):
            current = GPIO.input(button_pins[i])

            if current and not prev_button_states[i]:
                led_states[i] = not led_states[i]
                GPIO.output(led_pins[i], led_states[i])
                print(f"LED{i+1} status: {'ON' if led_states[i] else 'OFF'}")
                time.sleep(0.2)

            prev_button_states[i] = current

        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()
