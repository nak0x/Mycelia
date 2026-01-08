import json
from aiohttp import web
from app.ws_controllers.base import WsController
from app.frames.frame import Frame
from typing import List
import asyncio


class CoreController(WsController):

    def __init__(self, app: web.Application):
        super().__init__(app)
        # interaction 1
        self._shroom_forest_lighten = False
        self._wind_toggle = False
        self._rain_toggle = False
        self._interaction_1_done = False

        # interaction 2
        self._sphero_impact = False
        self._balance_toggle = False
        self._interaction_2_done = False

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

    # interaction 1
    async def on_shroom_forest_lighten(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        if frame.value == True:
            self._shroom_forest_lighten = True
            print(f"[WS] Shroom forest lighten set to True")
        await self._check_interaction_1(ws)
    
    async def on_wind_toggle(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        if frame.value == True:
            self._wind_toggle = True
            print(f"[WS] Wind toggle set to True")
        await self._check_interaction_1(ws)
    
    async def on_rain_toggle(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        if frame.value == True:
            self._rain_toggle = True
            print(f"[WS] Rain toggle set to True")
        await self._check_interaction_1(ws)

    async def _check_interaction_1(self, ws: web.WebSocketResponse) -> None:
        if self._interaction_1_done:
            return

        if self._shroom_forest_lighten and self._wind_toggle and self._rain_toggle:
            self._interaction_1_done = True
            # wait 10 seconds
            await asyncio.sleep(10)
            print("[WS] Interaction condition met! Broadcasting 01-interaction-done")
            # Broadcast to all clients
            message = json.dumps(self.build_frame("01-interaction-done", True))
            await self.hub.broadcast(message)

    # interaction 2
    async def on_sphero_impact(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        if frame.value == True:
            self._sphero_impact = True
            print(f"[WS] Sphero impact set to True")
        await self._check_interaction_2(ws)

    async def on_balance_toggle(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        if frame.value == True:
            self._balance_toggle = True
            print(f"[WS] Balance toggle set to True")
        await self._check_interaction_2(ws)

    async def _check_interaction_2(self, ws: web.WebSocketResponse) -> None:
        if self._interaction_2_done:
            return

        if self._sphero_impact and self._balance_toggle:
            self._interaction_2_done = True
            # wait 10 seconds
            await asyncio.sleep(10)
            print("[WS] Interaction condition met! Broadcasting 02-interaction-done")
            # Broadcast to all clients
            message = json.dumps(self.build_frame("02-interaction-done", True))
            await self.hub.broadcast(message)
            