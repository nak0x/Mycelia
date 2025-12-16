import asyncio
import time
import json
from datetime import datetime
from websockets.asyncio.server import serve
from aiohttp import web

CLIENTS = set()
CLIENTS_LOCK = asyncio.Lock()

ESP32_CLIENTS = set()
IOS_CLIENTS = set()

def build_led_message(value: bool = True) -> str:
    payload = {
        "metadata": {
            "senderId": "SERVER-020101",
            "timestamp": time.time(),
            "messageId": f"MSG-{datetime.now().isoformat()}-0001",
            "type": "ws-data",
            "receiverId": "ESP32-FF7700",
            "status": {"connection": 200},
        },
        "payload": [
            {
                "datatype": "boolean",
                "value": value,
                "slug": "led",
            }
        ],
    }
    return json.dumps(payload)

def build_robot_command(command: str, value: any, device_id: str = "IOS-APP-001") -> str:
    # Détermine le datatype selon la valeur
    if isinstance(value, bool):
        datatype = "bool"
    elif isinstance(value, int):
        datatype = "int"
    elif isinstance(value, float):
        datatype = "float"
    elif isinstance(value, list):
        datatype = "iarray"
    else:
        datatype = "string"
        value = str(value)
    
    payload = {
        "metadata": {
            "senderId": "SERVER-020101",
            "timestamp": time.time(),
            "messageId": f"MSG-{datetime.now().strftime('%Y%m%d')}-{int(time.time() * 1000) % 10000:04d}",
            "type": "ws-data",
            "receiverId": device_id,
            "status": {"connection": 200},
        },
        "payload": [
            {
                "datatype": datatype,
                "value": value,
                "slug": command,
            }
        ],
    }
    return json.dumps(payload)

async def send_to_esp32(message: str):
    """Envoie un message uniquement aux clients ESP32"""
    async with CLIENTS_LOCK:
        esp32_clients = list(ESP32_CLIENTS)

    if not esp32_clients:
        print("⚠️ Aucun client ESP32 connecté")
        return False

    results = await asyncio.gather(*(c.send(message) for c in esp32_clients), return_exceptions=True)
    ok = sum(1 for r in results if not isinstance(r, Exception))
    print(f"✅ Message ESP32 envoyé à {ok}/{len(esp32_clients)} client(s)")
    return ok > 0

async def send_to_ios(message: str):
    """Envoie un message uniquement aux clients iOS"""
    async with CLIENTS_LOCK:
        ios_clients = list(IOS_CLIENTS)

    if not ios_clients:
        print("⚠️ Aucun client iOS connecté")
        return False

    results = await asyncio.gather(*(c.send(message) for c in ios_clients), return_exceptions=True)
    ok = sum(1 for r in results if not isinstance(r, Exception))
    print(f"✅ Message iOS envoyé à {ok}/{len(ios_clients)} client(s)")
    return ok > 0

async def handler(websocket):
    # Track connections
    async with CLIENTS_LOCK:
        CLIENTS.add(websocket)

    client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    print(f"✅ Nouveau client: {client_info}")

    # Identification automatique via le path de connexion
    client_type = None
    path = websocket.request.path if hasattr(websocket, 'request') else websocket.path

    async with CLIENTS_LOCK:
        if "/esp32" in path.lower():
            ESP32_CLIENTS.add(websocket)
            client_type = "ESP32"
            print(f"   💡 Client auto-identifié comme ESP32 (via path: {path})")
        elif "/ios" in path.lower() or "/app" in path.lower():
            IOS_CLIENTS.add(websocket)
            client_type = "iOS"
            print(f"   📱 Client auto-identifié comme iOS (via path: {path})")
        else:
            print(f"   ⚠️ Client non identifié - path: {path}")
            print(f"   💡 Conseil: connectez-vous à ws://server:8000/esp32 ou ws://server:8000/ios")

    try:
        async for message in websocket:
            print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] Reçu de {client_info}:")

            try:
                # Parse le message JSON
                data = json.loads(message)

                # Affiche les infos de la frame
                metadata = data.get("metadata", {})
                payload = data.get("payload", [])

                sender_id = metadata.get('senderId', '')
                print(f"   Sender: {sender_id}")
                print(f"   Type: {metadata.get('type')}")
                print(f"   Payload: {payload}")

                # Détecte le type de client au premier message (fallback si pas identifié via path)
                if client_type is None and sender_id:
                    async with CLIENTS_LOCK:
                        if "ESP32" in sender_id.upper():
                            ESP32_CLIENTS.add(websocket)
                            client_type = "ESP32"
                            print(f"   💡 Client identifié comme ESP32 (via senderId)")
                        elif "IOS" in sender_id.upper() or "APP" in sender_id.upper():
                            IOS_CLIENTS.add(websocket)
                            client_type = "iOS"
                            print(f"   📱 Client identifié comme iOS (via senderId)")
                        else:
                            print(f"   ⚠️ Type de client inconnu pour senderId: {sender_id}")

                # Si c'est un état du robot, affiche les détails
                if metadata.get('type') == 'robot-state':
                    print("   📊 État du robot:")
                    for item in payload:
                        print(f"      - {item['slug']}: {item['value']}")

            except json.JSONDecodeError:
                print(f"   ⚠️ Message non-JSON: {message[:100]}")

    except Exception as ex:
        print(f"❌ Erreur/fermeture: {ex}")
    finally:
        async with CLIENTS_LOCK:
            CLIENTS.discard(websocket)
            if client_type == "ESP32":
                ESP32_CLIENTS.discard(websocket)
            elif client_type == "iOS":
                IOS_CLIENTS.discard(websocket)
        print(f"🔌 Client déconnecté: {client_info}")

async def trigger_interaction_1():
    """
    Séquence d'interaction-1:
    1. Allumer les LEDs (ESP32)
    2. Attendre 3 secondes
    3. Faire avancer le rover pendant 10 secondes (iOS)
    """
    print("\n" + "="*60)
    print("🎬 DÉCLENCHEMENT INTERACTION-1")
    print("="*60)

    # Étape 1: Allumer les LEDs
    print("💡 Étape 1/3: Allumage des LEDs...")
    led_msg = build_led_message(True)
    await send_to_esp32(led_msg)

    # Étape 2: Attendre 3 secondes
    print("⏳ Étape 2/3: Attente de 3 secondes...")
    await asyncio.sleep(3)

    # Étape 3: Faire avancer le rover pendant 10 secondes
    print("🤖 Étape 3/3: Avancement du rover pendant 10 secondes...")
    forward_msg = build_robot_command("forward", [100, 10], "IOS-APP-001")
    await send_to_ios(forward_msg)

    print("="*60)
    print("✅ INTERACTION-1 TERMINÉE")
    print("="*60 + "\n")

async def http_handler(request):
    """Handler pour les requêtes HTTP POST"""
    if request.method != 'POST':
        return web.Response(status=405, text="Method Not Allowed")

    try:
        data = await request.json()
        print(f"\n📨 Requête POST reçue: {json.dumps(data, indent=2)}")

        # Vérifie si c'est la trame attendue
        payload = data.get("payload", [])
        for item in payload:
            if item.get("slug") == "interaction-1" and item.get("value") == "done":
                print("🎯 Déclenchement de l'interaction-1 détecté!")
                # Lance l'interaction en arrière-plan
                asyncio.create_task(trigger_interaction_1())
                return web.json_response({"status": "success", "message": "Interaction-1 déclenchée"})

        return web.json_response({"status": "ignored", "message": "Payload non reconnu"})

    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")
    except Exception as e:
        print(f"❌ Erreur HTTP: {e}")
        return web.Response(status=500, text=str(e))

async def console_loop():
    """Boucle de commandes console"""
    print("\n" + "="*60)
    print("🎮 COMMANDES DISPONIBLES:")
    print("="*60)
    print("Mouvements:")
    print("  forward <speed> <duration>    -> avancer (ex: forward 100 10)")
    print("  backward <speed> <duration>   -> reculer (ex: backward 80 5)")
    print("  turn <degrees>     -> tourner (ex: turn 45)")
    print("  stop               -> arrêter")
    print()
    print("LED:")
    print("  led red            -> LED rouge")
    print("  led green          -> LED verte")
    print("  led blue           -> LED bleue")
    print("  led off            -> LED éteinte")
    print("  led <r,g,b>        -> LED couleur custom (ex: led 255,128,0)")
    print()
    print("Autres:")
    print("  clients            -> nombre de clients connectés")
    print("  quit               -> arrêter le serveur")
    print("="*60 + "\n")

    while True:
        cmd = (await asyncio.to_thread(input, "🎮 > ")).strip()

        if cmd == "quit":
            raise SystemExit(0)

        if cmd == "clients":
            async with CLIENTS_LOCK:
                print(f"📱 Clients connectés: {len(CLIENTS)}")
                print(f"   💡 ESP32: {len(ESP32_CLIENTS)}")
                print(f"   📱 iOS: {len(IOS_CLIENTS)}")
                print(f"   ❓ Non identifiés: {len(CLIENTS) - len(ESP32_CLIENTS) - len(IOS_CLIENTS)}")
            continue

        # Parse la commande
        parts = cmd.split()
        if len(parts) == 0:
            continue
        
        # Device ID cible (par défaut le rover)
        target_device = "IOS-APP-001"
        
        # Détermine la commande et la valeur
        command = None
        value = None
        
        if parts[0] == "forward":
            if len(parts) > 1:
                command = "forward"
                value = int(parts[1])
        
        elif parts[0] == "backward":
            if len(parts) > 1:
                command = "backward"
                value = int(parts[1])
        
        elif parts[0] == "turn":
            if len(parts) > 1:
                command = "turn"
                value = int(parts[1])
        
        elif parts[0] == "stop":
            command = "stop"
            value = True
        
        elif parts[0] == "led":
            if len(parts) > 1:
                if parts[1] == "red":
                    command = "led-red"
                    value = True
                elif parts[1] == "green":
                    command = "led-green"
                    value = True
                elif parts[1] == "blue":
                    command = "led-blue"
                    value = True
                elif parts[1] == "off":
                    command = "led-off"
                    value = True
                else:
                    # Couleur RGB personnalisée
                    command = "led"
                    value = parts[1]
        
        else:
            print("❌ Commande inconnue")
            continue
        
        if command is None or value is None:
            print("❌ Format de commande invalide")
            continue
        
        # Construit et envoie le message
        msg = build_robot_command(command, value, target_device)
        
        # Broadcast à tous les clients
        async with CLIENTS_LOCK:
            clients = list(CLIENTS)

        if not clients:
            print("⚠️ Aucun client connecté")
            continue

        results = await asyncio.gather(*(c.send(msg) for c in clients), return_exceptions=True)
        ok = sum(1 for r in results if not isinstance(r, Exception))
        print(f"✅ Envoyé à {ok}/{len(clients)} client(s)")

async def main():
    ws_port = 8000
    http_port = 8080

    # Configure le serveur HTTP
    app = web.Application()
    app.router.add_post('/trigger', http_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', http_port)

    # Démarre le serveur HTTP
    await site.start()
    print(f"🌐 Serveur HTTP démarré sur http://0.0.0.0:{http_port}")
    print(f"   📍 Endpoint: POST http://0.0.0.0:{http_port}/trigger")

    # Démarre le serveur WebSocket
    async with serve(handler, "0.0.0.0", ws_port) as server:
        print(f"🚀 Serveur WebSocket démarré sur ws://0.0.0.0:{ws_port}")
        print(f"📱 Prêt à recevoir des connexions (iOS + ESP32)")

        # Lance la boucle de console
        try:
            await console_loop()
        finally:
            await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Arrêt du serveur")