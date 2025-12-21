from aiohttp import web
from app.http_controllers.base import HttpController
from app.frames.parser import parse_frame_from_request


class CoreController(HttpController):

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
                text=self.build_frame("UNKNOWN", "error", "string", str(e), 400),
                status=400,
                content_type="application/json"
            )

        sent = await self.hub.broadcast(frame.raw_json)
        return web.json_response(self.build_frame(
            receiver_id=frame.metadata.get("senderId", "UNKNOWN"),
            slug="ws_sent",
            datatype="int",
            value=sent
        ))