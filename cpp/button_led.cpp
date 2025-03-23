#include <gpiod.h>
#include <iostream>
#include <unistd.h>

#define CHIPNAME "gpiochip0"
#define LED_LINE 4       // BCM 4? (GPIO 4)
#define BUTTON_LINE 15   // BCM 15? (GPIO 15)

int main() {
    gpiod_chip *chip;
    gpiod_line *led, *button;

    chip = gpiod_chip_open_by_name(CHIPNAME);
    if (!chip) {
        std::cerr << "Failed to open GPIO chip" << std::endl;
        return 1;
    }

    led = gpiod_chip_get_line(chip, LED_LINE);
    button = gpiod_chip_get_line(chip, BUTTON_LINE);

    gpiod_line_request_output(led, "led", 0);
    gpiod_line_request_input(button, "button");

    int prev_val = 0;
    bool light_on = false;

    while (true) {
        int val = gpiod_line_get_value(button);
        if (val == 1 && prev_val == 0) {
            light_on = !light_on;
            gpiod_line_set_value(led, light_on ? 1 : 0);
            std::cout << (light_on ? "LED ON" : "LED OFF") << std::endl;
        }
        prev_val = val;
        usleep(50000); // 50ms
    }

    gpiod_line_release(led);
    gpiod_line_release(button);
    gpiod_chip_close(chip);

    return 0;
}
