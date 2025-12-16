import asyncio
import time
import ssl
import argparse
import json
from datetime import datetime
from websockets.asyncio.server import serve
from aiohttp import web

# Global variables for server name
SERVER_ID = "SERVER-020201"
SERVER_3_ID = "SERVER-030201"
ESP32_EARTH_ID = "ESP32-020201"
ESP32_WATER_ID = "ESP32-020202"

CLIENTS = set()
CLIENTS_LOCK = asyncio.Lock()

ESP32_CLIENTS = set()
IOS_CLIENTS = set()

def build_led_message(value: bool = True) -> str:
    payload = {
        "metadata": {
            "senderId": SERVER_ID,
            "timestamp": time.time(),
            "messageId": f"MSG-{datetime.now().isoformat()}-0001",
            "type": "ws-data",
            "receiverId": ESP32_WATER_ID,
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

def build_interaction_done_message() -> str:
    payload = {
        "metadata": {
            "senderId": SERVER_ID,
            "timestamp": time.time(),
            "messageId": f"MSG-{datetime.now().isoformat()}-0002",
            "type": "ws-data",
            "receiverId": SERVER_3_ID,  # Modifiez avec l'ID de votre ESP cible
            "status": {"connection": 200},
        },
        "payload": [
            {
                "datatype": "string",
                "value": "done",
                "slug": "interaction-2",
            }
        ],
    }
    return json.dumps(payload)

def build_robot_command(command: str, value, device_id: str = "IOS-APP-001") -> str:
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
            "senderId": SERVER_ID,
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

async def broadcast(message: str, sender=None):
    # Snapshot des clients
    async with CLIENTS_LOCK:
        clients = list(CLIENTS)

    if not clients:
        return

    # Envoi en parallèle
    tasks = []
    for c in clients:
        if sender is not None and c is sender:
            continue
        tasks.append(asyncio.create_task(c.send(message)))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Nettoyage des sockets mortes
    dead = []
    for c, r in zip([c for c in clients if c is not sender], results):
        if isinstance(r, Exception):
            dead.append(c)

    if dead:
        async with CLIENTS_LOCK:
            for c in dead:
                CLIENTS.discard(c)

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

    balance_status = False
    sphero_status = False

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

                # Vérifier si le message contient balance ou sphero
                for item in payload:
                    if item.get("slug") == "balance" and item.get("value") is True:
                        print("🔄 BALANCE detected as TRUE")
                        balance_status = True
                    elif item.get("slug") == "sphero" and item.get("value") is True:
                        print("🟣 SPHERO detected as TRUE")
                        sphero_status = True

                # Si balance ET sphero sont true, envoyer interaction-2 done
                if balance_status and sphero_status:
                    print("\n" + "="*60)
                    print("✅ BALANCE + SPHERO = INTERACTION-2 DONE")
                    print("="*60)
                    done_message = build_interaction_done_message()
                    await broadcast(done_message, sender=websocket)
                    # Reset les statuts
                    balance_status = False
                    sphero_status = False
                    print("="*60 + "\n")

                # Si c'est un état du robot, affiche les détails
                if metadata.get('type') == 'robot-state':
                    print("   📊 État du robot:")
                    for item in payload:
                        print(f"      - {item['slug']}: {item['value']}")

            except json.JSONDecodeError:
                print(f"   ⚠️ Message non-JSON: {message[:100]}")

            await broadcast(message, sender=websocket)  # <-- Rebroadcast
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

async def console_loop():
    print("\n" + "="*60)
    print("🎮 COMMANDES DISPONIBLES:")
    print("="*60)
    print("LED:")
    print("  led on             -> allumer LED (ESP32)")
    print("  led off            -> éteindre LED (ESP32)")
    print()
    print("Broadcast:")
    print("  send <text>        -> broadcast raw text")
    print()
    print("Informations:")
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
        if cmd == "led on":
            msg = build_led_message(True)
        elif cmd == "led off":
            msg = build_led_message(False)
        elif cmd.startswith("send "):
            msg = cmd[5:]
        else:
            print("❌ Commande inconnue")
            continue

        # Broadcast to all connected clients
        async with CLIENTS_LOCK:
            clients = list(CLIENTS)

        if not clients:
            print("⚠️ Aucun client connecté")
            continue

        results = await asyncio.gather(*(c.send(msg) for c in clients), return_exceptions=True)
        ok = sum(1 for r in results if not isinstance(r, Exception))
        print(f"✅ Envoyé à {ok}/{len(clients)} client(s)")

async def main():
    parser = argparse.ArgumentParser(description="Args like --key=value")
    parser.add_argument("--ssl", action="store_true", help="Switch TLS on.")
    parser.add_argument("--ssl-keyfile", type=str, help="Server's secret key file.")
    parser.add_argument("--ssl-certfile", type=str, help="Server's certificate file.")
    parser.add_argument("--ssl-password", default=None, type=str, help="Pass phrase.")
    parser.add_argument("--ssl-ca-cert", type=str, help="CA's certificate.")
    parser.add_argument("--ssl-certs-reqs", type=int, default=0, help="Flag for certificate requires.")
    parser.add_argument("--port", type=int, default=8000, help="Port number")

    args = parser.parse_args()

    ssl_context = None
    if args.ssl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.verify_mode = args.ssl_certs_reqs
        ssl_context.load_cert_chain(
            certfile=args.ssl_certfile,
            keyfile=args.ssl_keyfile,
            password=args.ssl_password,
        )
        if args.ssl_certs_reqs:
            ssl_context.load_verify_locations(cafile=args.ssl_ca_cert)

    async with serve(handler, "0.0.0.0", args.port, ssl=ssl_context) as server:
        print(f"🚀 Serveur WebSocket démarré sur ws://0.0.0.0:{args.port}")
        print(f"📱 Prêt à recevoir des connexions (ESP32 + iOS)")
        print(f"")
        print(f"💡 Routes disponibles:")
        print(f"   - ws://0.0.0.0:{args.port}/esp32  (pour ESP32)")
        print(f"   - ws://0.0.0.0:{args.port}/ios    (pour iOS/App)")
        print(f"")
        # Run console loop alongside the server
        await console_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        pass
