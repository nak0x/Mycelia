# Script de test pour vérifier le bouton
# Upload ce fichier sur l'ESP32 et exécutez-le pour tester

from machine import Pin
import time

# Test avec PULL_DOWN (bouton connecté à 3.3V)
print("=== TEST BOUTON PULL_DOWN (connecté à 3.3V) ===")
button_down = Pin(5, Pin.IN, Pin.PULL_DOWN)

print("État initial:", button_down.value())
print("Appuyez sur le bouton plusieurs fois...")
print("Ctrl+C pour arrêter")

last_state = button_down.value()
try:
    while True:
        current_state = button_down.value()
        if current_state != last_state:
            if current_state == 1:
                print(">>> BOUTON PRESSÉ (state=1)")
            else:
                print(">>> BOUTON RELÂCHÉ (state=0)")
            last_state = current_state
        time.sleep(0.05)  # 50ms
except KeyboardInterrupt:
    print("\nTest arrêté")

print("\n" + "="*50)
print("=== TEST BOUTON PULL_UP (connecté à GND) ===")

# Test avec PULL_UP (bouton connecté à GND)
button_up = Pin(5, Pin.IN, Pin.PULL_UP)

print("État initial:", button_up.value())
print("Appuyez sur le bouton plusieurs fois...")
print("Ctrl+C pour arrêter")

last_state = button_up.value()
try:
    while True:
        current_state = button_up.value()
        if current_state != last_state:
            if current_state == 0:
                print(">>> BOUTON PRESSÉ (state=0)")
            else:
                print(">>> BOUTON RELÂCHÉ (state=1)")
            last_state = current_state
        time.sleep(0.05)  # 50ms
except KeyboardInterrupt:
    print("\nTest arrêté")
