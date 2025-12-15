import asyncio
from aiohttp import web
from typing import Optional


class WsHub:
    def __init__(self) -> None:
        self._clients: set[web.WebSocketResponse] = set()
        self._lock = asyncio.Lock()

    async def add(self, ws: web.WebSocketResponse) -> None:
        async with self._lock:
            self._clients.add(ws)

    async def remove(self, ws: web.WebSocketResponse) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def count(self) -> int:
        async with self._lock:
            return len(self._clients)

    async def broadcast(self, message: str, sender: Optional[web.WebSocketResponse] = None) -> int:
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
                await ws.send_str(message)
                sent += 1
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    self._clients.discard(ws)

        return sent