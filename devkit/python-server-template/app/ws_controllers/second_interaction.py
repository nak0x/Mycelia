from aiohttp import web
from app.ws_controllers.base import WsController
from app.frames.frame import Frame
import asyncio


class CoreController(WsController):

    def __init__(self, app: web.Application):
        super().__init__(app)

        self._sphero_impact = False
        self._balance_toggle = False
        self._interaction_2_done = False

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
            await self.hub.broadcast_action("02-interaction-done", True)
            