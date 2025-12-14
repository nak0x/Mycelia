import network
import time
from secrets import WIFI_SSID, WIFI_PASS

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connexion au WiFi en cours...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            time.sleep(1)
            
    if wlan.isconnected():
        print('Connecté !')
        print('Config réseau:', wlan.ifconfig())
        print(f"IP ESP32: {wlan.ifconfig()[0]}") 
    else:
        print('Echec de connexion WiFi.')

connect_wifi()
