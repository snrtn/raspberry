#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>
#include <stdbool.h>

#define CHIPNAME "gpiochip0"
#define LED_LINE 4       // BCM 4? (GPIO 4)
#define BUTTON_LINE 15   // BCM 15? (GPIO 15)

int main() {
    struct gpiod_chip *chip;
    struct gpiod_line *led, *button;
    int val;
    bool light_on = false;

    chip = gpiod_chip_open_by_name(CHIPNAME);

    led = gpiod_chip_get_line(chip, LED_LINE);
    button = gpiod_chip_get_line(chip, BUTTON_LINE);

    gpiod_line_request_output(led, "led", 0);
    gpiod_line_request_input(button, "button");

    int prev_val = 0;

    while (1) {
        val = gpiod_line_get_value(button);
        if (val == 1 && prev_val == 0) {
            light_on = !light_on;
            gpiod_line_set_value(led, light_on ? 1 : 0);
            printf(light_on ? "LED ON\n" : "LED OFF\n");
        }
        prev_val = val;
        usleep(50000); // 50ms
    }

    gpiod_line_release(led);
    gpiod_line_release(button);
    gpiod_chip_close(chip);
    return 0;
}
