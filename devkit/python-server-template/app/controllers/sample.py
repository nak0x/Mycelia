import json
import time
from datetime import datetime
from aiohttp import web

from app.controllers.base import BaseController
from app.frames.parser import parse_frame_from_request
from app.frames.factory import ok_frame


class SampleController(BaseController):

    async def led(self, request: web.Request) -> web.Response:
        """
        Expects a Frame in HTTP body.
        Reads payload slug=led value:boolean and rebroadcasts a standardized led frame to WS clients.
        """
        frame = await parse_frame_from_request(request)

        led_value = None
        for p in frame.payloads:
            if p.get("slug") == "led":
                led_value = bool(p.get("value"))
                break

        if led_value is None:
            return web.json_response(ok_frame(
                sender=self.server_id,
                receiver=frame.metadata.get("senderId", "UNKNOWN"),
                connection_status=422,
                payload=[{"datatype": "string", "value": "Missing payload slug=led", "slug": "warning"}]
            ), status=422)

        outgoing = self._build_led_frame(value=led_value)
        sent = await self.hub.broadcast(outgoing)

        return web.json_response(ok_frame(
            sender=self.server_id,
            receiver=frame.metadata.get("senderId", "UNKNOWN"),
            payload=[
                {"datatype": "boolean", "value": led_value, "slug": "led"},
                {"datatype": "integer", "value": sent, "slug": "ws_sent"}
            ]
        ))

    def _build_led_frame(self, value: bool) -> str:
        payload = {
            "metadata": {
                "senderId": self.server_id,
                "timestamp": time.time(),
                "messageId": f"MSG-{datetime.now().isoformat()}-0001",
                "type": "ws-data",
                "receiverId": "ESP32-FF7700",
                "status": {"connection": 200},
            },
            "payload": [
                {"datatype": "boolean", "value": value, "slug": "led"}
            ],
        }
        return json.dumps(payload)