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
        self.on_message_received = None # Callback function

    async def register(self, websocket):
        async with self.lock:
            self.clients.add(websocket)
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"✅ Nouveau client: {client_info}")
        
        # Auto-identification
        client_type = None
        path = websocket.request.path if hasattr(websocket, 'request') else websocket.path
        
        async with self.lock:
            if "/esp32" in path.lower():
                self.esp32_clients.add(websocket)
                client_type = "ESP32"
                print(f"   💡 Client auto-identifié comme ESP32 (via path: {path})")
            elif "/ios" in path.lower() or "/app" in path.lower():
                self.ios_clients.add(websocket)
                client_type = "iOS"
                print(f"   📱 Client auto-identifié comme iOS (via path: {path})")
            else:
                print(f"   ⚠️ Client non identifié - path: {path}")
                print(f"   💡 Conseil: connectez-vous à ws://server:8000/esp32 ou ws://server:8000/ios")
        
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

    async def broadcast(self, message, sender=None):
        async with self.lock:
            clients = list(self.clients)
        
        if not clients:
            return

        tasks = []
        for c in clients:
            if sender is not None and c is sender:
                continue
            tasks.append(asyncio.create_task(c.send(message)))
        
        if not tasks:
            return

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Cleanup dead connections
        dead = []
        target_clients = [c for c in clients if c is not sender]
        for c, r in zip(target_clients, results):
            if isinstance(r, Exception):
                dead.append(c)
        
        if dead:
            async with self.lock:
                for c in dead:
                    self.clients.discard(c)
                    self.esp32_clients.discard(c)
                    self.ios_clients.discard(c)

    async def handler(self, websocket):
        client_type, client_info = await self.register(websocket)
        
        try:
            async for message in websocket:
                print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] Reçu de {client_info}:")
                
                # Rebroadcast immediately (as per original logic)
                await self.broadcast(message, sender=websocket)

                try:
                    data = json.loads(message)
                    metadata = data.get("metadata", {})
                    sender_id = metadata.get('senderId', '')
                    
                    # Identification fallback
                    if client_type is None and sender_id:
                        client_type = await self.identify_client(websocket, sender_id)

                    # External Logic Callback
                    if self.on_message_received:
                        await self.on_message_received(websocket, data)

                except json.JSONDecodeError:
                    print(f"   ⚠️ Message non-JSON: {message[:100]}")
        except Exception as ex:
            print(f"❌ Erreur/fermeture: {ex}")
        finally:
            await self.unregister(websocket, client_type, client_info)

    def start_server(self, port, ssl_context=None):
        return serve(self.handler, "0.0.0.0", port, ssl=ssl_context)
