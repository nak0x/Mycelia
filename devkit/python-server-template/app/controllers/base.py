from aiohttp import web
from app.ws_hub import WsHub


class BaseController:
    """
    Framework controller base class.
    A controller is created once and reused (singleton per class).
    It can access:
      - self.app
      - self.hub (WS broadcast)
    """

    def __init__(self, app: web.Application):
        self.app = app

    @property
    def hub(self) -> WsHub:
        return self.app["hub"]
    
    @property
    def server_id(self) -> str:
        return self.app["server_id"]