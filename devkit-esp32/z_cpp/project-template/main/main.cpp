#include <cstdio>
#include <string>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char* TAG = "main";

extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "Hello from C++ on ESP32!");

    int counter = 0;

    while (true) {
        std::string msg = "Tick number: " + std::to_string(counter);
        ESP_LOGI(TAG, "%s", msg.c_str());

        counter++;
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

