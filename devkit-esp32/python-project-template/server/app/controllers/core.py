from aiohttp import web
from app.controllers.base import BaseController
from app.frames.parser import parse_frame_from_request
from app.frames.factory import ok_frame, error_frame_json


class CoreController(BaseController):

    async def health(self, request: web.Request) -> web.Response:
        # Health does not need Frame input, but still returns a Frame-like JSON if you want.
        return web.json_response({
            "ok": True,
            "service": "unified-server"
        })

    async def broadcast(self, request: web.Request) -> web.Response:
        """
        Expects a Frame in HTTP body.
        Broadcasts the exact same validated frame to WS clients.
        """
        try:
            frame = await parse_frame_from_request(request)
        except Exception as e:
            return web.Response(
                text=error_frame_json("SERVER", "UNKNOWN", f"Invalid frame: {e}", 400),
                status=400,
                content_type="application/json"
            )

        sent = await self.hub.broadcast(frame.raw_json)
        return web.json_response(ok_frame(
            sender="SERVER",
            receiver=frame.metadata.get("senderId", "UNKNOWN"),
            payload=[
                {"datatype": "integer", "value": sent, "slug": "ws_sent"}
            ]
        ))