import asyncio
import argparse
import ssl
from .core.websocket_manager import WebSocketManager
from .controllers.interaction_controller import InteractionController
from .utils.messages import build_led_message
from .config import WS_PORT, HTTP_PORT

async def console_loop(ws_manager, controller):
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
    print("  reset              -> reset balance et sphero")
    print("  quit               -> arrêter le serveur")
    print("="*60 + "\n")

    while True:
        try:
            cmd = (await asyncio.to_thread(input, "🎮 > ")).strip()
        except EOFError:
            break

        if cmd == "quit":
            raise SystemExit(0)

        if cmd == "clients":
            async with ws_manager.lock:
                print(f"📱 Clients connectés: {len(ws_manager.clients)}")
                print(f"   💡 ESP32: {len(ws_manager.esp32_clients)}")
                print(f"   📱 iOS: {len(ws_manager.ios_clients)}")
            continue

        if cmd == "reset":
            controller.reset()
            print("✅ Balance et Sphero réinitialisés")
            continue

        msg = None
        if cmd == "led on":
            msg = build_led_message(True)
        elif cmd == "led off":
            msg = build_led_message(False)
        elif cmd.startswith("send "):
            msg = cmd[5:]
        else:
            print("❌ Commande inconnue")
            continue

        await ws_manager.broadcast(msg)
        print(f"✅ Message envoyé")

async def main():
    parser = argparse.ArgumentParser(description="Terre WS Server")
    parser.add_argument("--ssl", action="store_true", help="Switch TLS on.")
    parser.add_argument("--ssl-keyfile", type=str, help="Server's secret key file.")
    parser.add_argument("--ssl-certfile", type=str, help="Server's certificate file.")
    parser.add_argument("--ssl-password", default=None, type=str, help="Pass phrase.")
    parser.add_argument("--ssl-ca-cert", type=str, help="CA's certificate.")
    parser.add_argument("--ssl-certs-reqs", type=int, default=0, help="Flag for certificate requires.")
    parser.add_argument("--port", type=int, default=WS_PORT, help="Port number")

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

    # 1. Init Manager
    ws_manager = WebSocketManager()
    
    # 2. Init Controller & Bind Callback
    controller = InteractionController(ws_manager)
    ws_manager.on_message_received = controller.handle_message

    # 3. Start Server
    async with ws_manager.start_server(args.port, ssl_context) as server:
        print(f"🚀 Serveur WebSocket démarré sur ws://0.0.0.0:{args.port}")
        print(f"📱 Prêt à recevoir des connexions (ESP32 + iOS)")
        print(f"Routes: /esp, /ios")
        
        # 4. Run Console
        try:
            await console_loop(ws_manager, controller)
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Arrêt du serveur")
