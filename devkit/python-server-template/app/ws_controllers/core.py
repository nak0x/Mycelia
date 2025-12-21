import json
from aiohttp import web
from app.ws_controllers.base import WsController
from app.frames.frame import Frame


class CoreController(WsController):

    async def on_ping(self, frame: Frame, ws: web.WebSocketResponse) -> None:
        sender = frame.metadata.get("senderId", "UNKNOWN")
        print("[WS] PING received from", sender)
        await ws.send_str(json.dumps(self.build_frame("pong", "pong")))