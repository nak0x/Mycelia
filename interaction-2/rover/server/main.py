import asyncio
from aiohttp import web
from .core.websocket_manager import WebSocketManager
from .core.http_server import HTTPServer
from .controllers.interaction_controller import InteractionController
from .utils.messages import build_robot_command
from .config import WS_PORT, HTTP_PORT, DEFAULT_IOS_TARGET

async def console_loop(ws_manager):
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

        # Parse la commande
        parts = cmd.split()
        if len(parts) == 0:
            continue
        
        target_device = DEFAULT_IOS_TARGET
        
        command = None
        value = None
        
        if parts[0] == "forward" and len(parts) > 1:
            command = "forward"
            value = int(parts[1])
        elif parts[0] == "backward" and len(parts) > 1:
            command = "backward"
            value = int(parts[1])
        elif parts[0] == "turn" and len(parts) > 1:
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
        await ws_manager.broadcast(msg)

async def main():
    # 1. Init WebSocket Manager
    ws_manager = WebSocketManager()
    
    # 2. Init Controllers
    interaction_controller = InteractionController(ws_manager)
    
    # 3. Configure HTTP Routes
    http_routes = [
        web.post('/trigger', interaction_controller.http_trigger_handler)
    ]
    
    # 4. Start HTTP Server
    http_server = HTTPServer(HTTP_PORT, http_routes)
    await http_server.start()
    print(f"   📍 Endpoint: POST http://0.0.0.0:{HTTP_PORT}/trigger")

    # 5. Start WebSocket Server
    async with ws_manager.start_server(WS_PORT) as server:
        print(f"🚀 Serveur WebSocket démarré sur ws://0.0.0.0:{WS_PORT}")
        print(f"📱 Prêt à recevoir des connexions (iOS + ESP32)")

        # 6. Run Console Loop
        try:
            await console_loop(ws_manager)
        finally:
            await http_server.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Arrêt du serveur")
