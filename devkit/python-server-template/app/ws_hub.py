import json
import asyncio
from aiohttp import web
from typing import Optional
from app.frames.factory import frame

class WsHub:
    def __init__(self, app: web.Application) -> None:
        self.app = app
        self._setted_clients: dict = {}
        self._clients: set[web.WebSocketResponse] = set()
        self._lock = asyncio.Lock()

    async def set_client(self, id: str, ws: web.WebSocketResponse) -> None:
        async with self._lock:
            if ws not in self._clients:
                return
            print(f"[WS] New client setted: {id}.")
            self._setted_clients[id] = ws

        await self.broadcast_action("00-new-client", id)

    async def unset_client(self, ws: web.WebSocketResponse) -> Optional[str]:
        async with self._lock:
            for id, client in self._setted_clients.items():
                if client == ws:
                    self._setted_clients[id] = None
                    print(f"[WS] client disconnected: {id}.")
                    return id
        return None

    async def add(self, ws: web.WebSocketResponse) -> None:
        async with self._lock:
            print("[WS] New client connected.")
            self._clients.add(ws)

    async def remove(self, ws: web.WebSocketResponse) -> None:
        client_id = await self.unset_client(ws)
        print(f"[WS] {client_id}")
        await self.broadcast_action("00-lost-client", client_id)

        async with self._lock:
            if not client_id:
                print("[WS] client disconnected.")
            self._clients.discard(ws)

    async def count(self) -> int:
        async with self._lock:
            return len(self._clients)
        
    async def send_json(self, ws: web.WebSocketResponse, obj: dict) -> None:
        message = json.dumps(obj, ensure_ascii=False)
        await self.send_message(ws, message)
    
    async def send_message(self, ws: web.WebSocketResponse, message: str, can_print: bool = True) -> None:
        await ws.send_str(message)
        if can_print:
            print(f"> {message}")

    async def send_action(self, ws: web.WebSocketResponse, action: str, value) -> None:
        message = json.dumps(frame(
            sender=self.app["server_id"],
            action=action,
            value=value
        ))
        await self.send_message(ws, message)

    async def broadcast_action(self, action: str, value) -> int:
        message = json.dumps(frame(
            sender=self.app["server_id"],
            action=action,
            value=value
        ))
        return await self.broadcast(message)

    async def broadcast(self, message: str) -> int:
        async with self._lock:
            clients = list(self._clients)

        if not clients:
            return 0

        dead: list[web.WebSocketResponse] = []
        sent = 0

        for ws in clients:
            if sender is not None and ws is sender:
                continue
            if ws.closed:
                dead.append(ws)
                continue
            try:
                await self.send_message(ws, message, sent == 0)
                sent += 1
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    self._clients.discard(ws)

        return sent