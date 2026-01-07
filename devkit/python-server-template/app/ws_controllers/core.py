import json
from aiohttp import web
from app.ws_controllers.base import WsController
from app.frames.frame import Frame


class CoreController(WsController):

    def __init__(self, app: web.Application):
        super().__init__(app)
        self._sphero_impact = False
        self._balance_toggle = False

    async def on_ping(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        sender = frame.metadata.get("senderId", "UNKNOWN")
        print("[WS] PING received from", sender)
        await ws.send_str(json.dumps(self.build_frame("pong", "pong")))

    async def on_sphero_impact(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        if frame.value == True:
            self._sphero_impact = True
            print(f"[WS] Sphero impact set to True")
        await self._check_interaction(ws)

    async def on_balance_toggle(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        if frame.value == True:
            self._balance_toggle = True
            print(f"[WS] Balance toggle set to True")
        await self._check_interaction(ws)

    async def _check_interaction(self, ws: web.WebSocketResponse) -> None:
        if self._sphero_impact and self._balance_toggle:
            print("[WS] Interaction condition met! Broadcasting 02-interaction-done")
            # Broadcast to all clients
            message = json.dumps(self.build_frame("02-interaction-done", True))
            await self.hub.broadcast(message)
            
            # Reset state if needed (optional, depending on requirements. 
            # I'll keep them true until explicitly set false by new messages, 
            # or maybe reset them to avoid repeated triggers?
            # The prompt says "Quand on recoit ... a True", implies a state change.
            # I will not auto-reset for now, assuming the client sends False when done or state changes.)