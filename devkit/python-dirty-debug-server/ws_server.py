import asyncio
import time
import ssl
import json
import inspect
from typing import Optional, Callable, Awaitable, Dict, Any
from datetime import datetime
from websockets.asyncio.server import serve
from console_loop import ConsoleLoop


PayloadHandler = Callable[[Dict[str, Any], Dict[str, Any], Any], Awaitable[None] | None]


class WebSocketServer:
    def __init__(self):
        self.clients = set()
        self.clients_lock = asyncio.Lock()
        self.console_loop = ConsoleLoop(self)
        self.server_id = "SERVER-0E990F"
        self.payload_handlers: Dict[str, PayloadHandler] = {}

    def build_payload_dict(
        self,
        *,
        slug: str,
        value,
        datatype: str,
        receiver_id: str,
        message_type: str = "ws-data",
    ) -> dict:
        return {
            "metadata": {
                "senderId": self.server_id,
                "timestamp": time.time(),
                "messageId": f"MSG-{datetime.now().isoformat()}-0001",
                "type": message_type,
                "receiverId": receiver_id,
                "status": {"connection": 200},
            },
            "payload": [
                {
                    "datatype": datatype,
                    "value": value,
                    "slug": slug,
                }
            ],
        }

    def build_payload_message(self, **kwargs) -> str:
        payload = self.build_payload_dict(**kwargs)
        return json.dumps(payload)

    def build_led_message(self, value: bool = True) -> str:
        return self.build_payload_message(
            slug="led",
            value=value,
            datatype="boolean",
            receiver_id="ESP32-FF7700",
        )

    def register_payload_handler(self, slug: str, handler: PayloadHandler):
        """Register a callback that runs when a matching payload slug is received."""
        self.payload_handlers[slug] = handler

    async def handler(self, websocket):
        # Track connections
        async with self.clients_lock:
            self.clients.add(websocket)

        ssl_object = websocket.transport.get_extra_info("ssl_object")
        if ssl_object:
            client_cert = ssl_object.getpeercert()
            common_name = None
            if client_cert:
                subject = client_cert.get("subject", [])
                for item in subject:
                    for attr in item:
                        if attr[0].lower() == "commonname":
                            common_name = attr[1]
                            break
                    if common_name:
                        break
            print(f"New client: {common_name}")
        else:
            print("New anonymous client.")

        try:
            async for message in websocket:
                print(f"{datetime.now().isoformat()} | recv: {message}")
                await self._process_incoming_message(message, websocket)
        except Exception as ex:
            print(f"Connection error/closed: {ex}")
        finally:
            async with self.clients_lock:
                self.clients.discard(websocket)
            print("Client disconnected.")

    async def _process_incoming_message(self, raw_message: str, websocket):
        """Handle inbound payloads and execute registered callbacks."""
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError:
            print("Received non-JSON payload; ignoring.")
            return

        metadata = data.get("metadata", {})
        if metadata.get("receiverId") != self.server_id:
            # Not intended for this server
            return

        payloads = data.get("payload", [])
        if not isinstance(payloads, list):
            print("Payload field is not a list; ignoring.")
            return

        for payload_entry in payloads:
            slug = payload_entry.get("slug")
            if not slug:
                continue
            handler = self.payload_handlers.get(slug)
            if not handler:
                continue
            try:
                result = handler(payload_entry, metadata, websocket)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:
                print(f"Handler error for slug '{slug}': {exc}")

    def _create_ssl_context(self, ssl_enabled: bool, ssl_keyfile: str = None, 
                           ssl_certfile: str = None, ssl_password: str = None,
                           ssl_ca_cert: str = None, ssl_certs_reqs: int = 0) -> Optional[ssl.SSLContext]:
        if not ssl_enabled:
            return None
        
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.verify_mode = ssl_certs_reqs
        ssl_context.load_cert_chain(
            certfile=ssl_certfile,
            keyfile=ssl_keyfile,
            password=ssl_password,
        )
        if ssl_certs_reqs:
            ssl_context.load_verify_locations(cafile=ssl_ca_cert)
        
        return ssl_context

    async def run(self, host: str = "0.0.0.0", port: int = 8000, 
                  ssl_enabled: bool = False, ssl_keyfile: str = None,
                  ssl_certfile: str = None, ssl_password: str = None,
                  ssl_ca_cert: str = None, ssl_certs_reqs: int = 0):
        ssl_context = self._create_ssl_context(
            ssl_enabled, ssl_keyfile, ssl_certfile, 
            ssl_password, ssl_ca_cert, ssl_certs_reqs
        )

        async with serve(self.handler, host, port, ssl=ssl_context) as server:
            print(f"Server started on {host}:{port}")
            # Run console loop alongside the server
            await self.console_loop.run()

