import asyncio
import time
import ssl
import argparse
import json
from datetime import datetime
from websockets.asyncio.server import serve

CLIENTS = set()
CLIENTS_LOCK = asyncio.Lock()

def build_led_message(value: bool = True) -> str:
    payload = {
        "metadata": {
            "senderId": "SERVER-0E990F",
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

def build_interaction_done_message() -> str:
    payload = {
        "metadata": {
            "senderId": "SERVER-0E990F",
            "timestamp": time.time(),
            "messageId": f"MSG-{datetime.now().isoformat()}-0002",
            "type": "ws-data",
            "receiverId": "ESP32-TARGET",  # Modifiez avec l'ID de votre ESP cible
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
    async with CLIENTS_LOCK:
        CLIENTS.add(websocket)

    print("New client.")

    try:
        async for message in websocket:
            print(f"{datetime.now().isoformat()} | recv: {message}")

            # Vérifier si le message contient led: true
            try:
                data = json.loads(message)
                if "payload" in data:
                    for item in data["payload"]:
                        if item.get("slug") == "led" and item.get("value") is True:
                            print("LED detected as TRUE - sending interaction-2 done message")
                            done_message = build_interaction_done_message()
                            await broadcast(done_message, sender=websocket)
            except json.JSONDecodeError:
                pass  # Si ce n'est pas du JSON, on continue normalement

            await broadcast(message, sender=websocket)  # <-- ICI: rebroadcast
    except Exception as ex:
        print(f"Connection error/closed: {ex}")
    finally:
        async with CLIENTS_LOCK:
            CLIENTS.discard(websocket)
        print("Client disconnected.")

async def console_loop():
    print("Console commands:")
    print("  led on    -> send led_on=true")
    print("  led off   -> send led_on=false")
    print("  send <text> -> broadcast raw text")
    print("  clients   -> show connected client count")
    print("  quit      -> stop server")

    while True:
        cmd = (await asyncio.to_thread(input, "> ")).strip()

        if cmd == "quit":
            raise SystemExit(0)

        if cmd == "clients":
            async with CLIENTS_LOCK:
                print(f"Connected clients: {len(CLIENTS)}")
            continue

        if cmd == "led on":
            msg = build_led_message(True)
        elif cmd == "led off":
            msg = build_led_message(False)
        elif cmd.startswith("send "):
            msg = cmd[5:]
        else:
            print("Unknown command.")
            continue

        # Broadcast to all connected clients
        async with CLIENTS_LOCK:
            clients = list(CLIENTS)

        if not clients:
            print("No clients connected.")
            continue

        results = await asyncio.gather(*(c.send(msg) for c in clients), return_exceptions=True)
        ok = sum(1 for r in results if not isinstance(r, Exception))
        print(f"Sent to {ok}/{len(clients)} clients.")

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
        print(f"Server started on 0.0.0.0:{args.port}")
        # Run console loop alongside the server
        await console_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        pass
