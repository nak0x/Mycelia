import socket
import json
import time
import machine
import neopixel

PIN_NEOPIXEL = 4
NUM_LEDS = 100
SERVER_PORT = 8080

np = neopixel.NeoPixel(machine.Pin(PIN_NEOPIXEL), NUM_LEDS)

def set_leds_color(r, g, b):
    """Allume tout le bandeau led"""
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)
    np.write()

def clear_leds():
    """Éteint tout"""
    set_leds_color(0, 0, 0)

def create_response_json(status_code, receiver_id):
    """Génère la trame de réponse"""
    return json.dumps({
        "metadata": {
            "senderId": "ESP32-SERVER",
            "timestamp": int(time.time()),
            "messageId": f"MSG-{int(time.time())}",
            "type": "up",
            "receiverId": receiver_id,
            "status": {
                "connection": status_code
            }
        },
        "payload": []
    })


def start_server():
    addr = socket.getaddrinfo('0.0.0.0', SERVER_PORT)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    
    print(f"Serveur en écoute sur le port {SERVER_PORT}...")

    while True:
        try:
            cl, addr = s.accept()
            print('Client connecté depuis', addr)
            
            request = cl.recv(1024)
            request_str = request.decode('utf-8')
            
            json_start = request_str.find('{')
            if json_start != -1:
                json_str = request_str[json_start:]
            else:
                json_str = request_str

            try:
                data = json.loads(json_str)
                print("JSON Reçu:", data)
                
                sender_id = data.get('metadata', {}).get('senderId', 'UNKNOWN')
                payload = data.get('payload', [])
                
                action_found = False
                for item in payload:
                    if item.get('slug') == 'a_led' and item.get('value') in ["ON"]:
                        print(">> ACTION: Allumage des LEDs")
                        set_leds_color(0, 200, 200)
                        action_found = True
                    elif item.get('slug') == 'a_led' and item.get('value') == "OFF":
                        print(">> ACTION: Extinction")
                        clear_leds()
                        action_found = True

                response = create_response_json(200 if action_found else 218, sender_id)
                cl.send(response.encode('utf-8'))
                
            except ValueError as e:
                print("Erreur de parsing JSON", e)
                cl.send(create_response_json(400, "UNKNOWN").encode('utf-8'))
                
            cl.close()
            
        except OSError as e:
            print("Erreur Socket:", e)
            cl.close()

# Démarrage
try:
    start_server()
except KeyboardInterrupt:
    print("Arrêt du serveur")
