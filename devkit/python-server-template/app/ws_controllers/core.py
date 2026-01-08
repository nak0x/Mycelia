import json
from aiohttp import web
from app.ws_controllers.base import WsController
from app.frames.frame import Frame
from typing import List
import asyncio


class CoreController(WsController):

    async def on_ping(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        print("[WS] PING received from", frame.sender_id)
        await ws.send_str(json.dumps(self.build_frame("pong", "pong")))

    async def on_new_connection(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        await self.hub.set_client(frame.sender_id, ws)

    async def on_get_connected_clients(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        data: List[dict] = []
        for id, client in self.hub._setted_clients.items():
            data.append({
                "clientId": id,
                "isConnected": client is not None
            })
        await ws.send_str(json.dumps(self.build_frame("connected-clients", data)))