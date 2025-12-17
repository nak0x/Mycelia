import asyncio
import json
from datetime import datetime
from websockets.asyncio.server import serve

class WebSocketManager:
    def __init__(self):
        self.clients = set()
        self.esp32_clients = set()
        self.ios_clients = set()
        self.lock = asyncio.Lock()

    async def register(self, websocket):
        async with self.lock:
            self.clients.add(websocket)
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"✅ Nouveau client: {client_info}")
        
        # Auto-identification via path
        client_type = None
        path = websocket.request.path if hasattr(websocket, 'request') else websocket.path
        
        async with self.lock:
            if "/esp" in path.lower():
                self.esp32_clients.add(websocket)
                client_type = "ESP32"
                print(f"   💡 Client auto-identifié comme ESP32 (via path: {path})")
            elif "/ios" in path.lower() or "/app" in path.lower():
                self.ios_clients.add(websocket)
                client_type = "iOS"
                print(f"   📱 Client auto-identifié comme iOS (via path: {path})")
            else:
                print(f"   ⚠️ Client non identifié - path: {path}")
                print(f"   💡 Conseil: connectez-vous à ws://server:8000/esp ou ws://server:8000/ios")
        
        return client_type, client_info

    async def unregister(self, websocket, client_type, client_info):
        async with self.lock:
            self.clients.discard(websocket)
            if client_type == "ESP32":
                self.esp32_clients.discard(websocket)
            elif client_type == "iOS":
                self.ios_clients.discard(websocket)
        print(f"🔌 Client déconnecté: {client_info}")

    async def identify_client(self, websocket, sender_id):
        """Identifie un client sur base du senderId du premier message"""
        client_type = None
        async with self.lock:
            if "ESP32" in sender_id.upper():
                self.esp32_clients.add(websocket)
                client_type = "ESP32"
                print(f"   💡 Client identifié comme ESP32 (via senderId)")
            elif "IOS" in sender_id.upper() or "APP" in sender_id.upper():
                self.ios_clients.add(websocket)
                client_type = "iOS"
                print(f"   📱 Client identifié comme iOS (via senderId)")
            else:
                print(f"   ⚠️ Type de client inconnu pour senderId: {sender_id}")
        return client_type

    async def broadcast(self, message):
        async with self.lock:
            clients = list(self.clients)
        
        if not clients:
            print("⚠️ Aucun client connecté pour broadcast")
            return 0

        results = await asyncio.gather(*(c.send(message) for c in clients), return_exceptions=True)
        return sum(1 for r in results if not isinstance(r, Exception))

    async def send_to_esp32(self, message):
        async with self.lock:
            clients = list(self.esp32_clients)
        
        if not clients:
            print("⚠️ Aucun client ESP32 connecté")
            return False

        results = await asyncio.gather(*(c.send(message) for c in clients), return_exceptions=True)
        ok = sum(1 for r in results if not isinstance(r, Exception))
        print(f"✅ Message ESP32 envoyé à {ok}/{len(clients)} client(s)")
        return ok > 0

    async def send_to_ios(self, message):
        async with self.lock:
            clients = list(self.ios_clients)
        
        if not clients:
            print("⚠️ Aucun client iOS connecté")
            return False

        results = await asyncio.gather(*(c.send(message) for c in clients), return_exceptions=True)
        ok = sum(1 for r in results if not isinstance(r, Exception))
        print(f"✅ Message iOS envoyé à {ok}/{len(clients)} client(s)")
        return ok > 0

    async def handler(self, websocket):
        client_type, client_info = await self.register(websocket)
        
        try:
            async for message in websocket:
                print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] Reçu de {client_info}:")
                try:
                    data = json.loads(message)
                    metadata = data.get("metadata", {})
                    payload = data.get("payload", [])
                    sender_id = metadata.get('senderId', '')
                    
                    print(f"   Sender: {sender_id}")
                    print(f"   Type: {metadata.get('type')}")
                    print(f"   Payload: {payload}")

                    if client_type is None and sender_id:
                        client_type = await self.identify_client(websocket, sender_id)

                    if metadata.get('type') == 'robot-state':
                        print("   📊 État du robot:")
                        for item in payload:
                            print(f"      - {item['slug']}: {item['value']}")

                except json.JSONDecodeError:
                    print(f"   ⚠️ Message non-JSON: {message[:100]}")
        except Exception as ex:
            print(f"❌ Erreur connexion: {ex}")
        finally:
            await self.unregister(websocket, client_type, client_info)

    def start_server(self, port):
        return serve(self.handler, "0.0.0.0", port)
