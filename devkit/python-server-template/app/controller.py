from aiohttp import web
from app.ws_hub import WsHub
from app.frames.factory import frame
from typing import Any, Dict

class Controller:
    def __init__(self, app: web.Application):
        self.app = app

    @property
    def hub(self) -> WsHub:
        return self.app["hub"]
    
    @property
    def server_id(self) -> str:
        return self.app["server_id"]
    
    def build_frame(self, receiver_id: str, slug: str, datatype: str, value: Any, connection_status: int = 200) -> Dict[str, Any]:
        return frame(
            sender=self.server_id,
            receiver=receiver_id,
            slug=slug,
            datatype=datatype,
            value=value,
            connection_status=connection_status
        )