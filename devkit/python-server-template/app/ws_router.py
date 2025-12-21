from __future__ import annotations
from aiohttp import web

from app.import_utils import import_symbol
from app.frames.frame import Frame
from app.config import AppConfig
from app.ws_controllers.base import WsController


class WsActionDispatcher:
    def __init__(self, app: web.Application, cfg: AppConfig):
        self.app = app
        self.cfg = cfg
        self._controller_cache: dict[str, WsController] = {}

    def _get_controller(self, import_path: str) -> WsController:
        if import_path not in self._controller_cache:
            ControllerClass = import_symbol(import_path)
            self._controller_cache[import_path] = ControllerClass(self.app)
        return self._controller_cache[import_path]

    async def dispatch(self, frame: Frame, ws: web.WebSocketResponse) -> bool:
        """
        Returns True if a handler was called, False otherwise.
        """
        route = self.cfg.ws_actions.get(frame.action)
        if route is None:
            return False

        controller = self._get_controller(route.controller)

        if not hasattr(controller, route.action):
            raise RuntimeError(
                f"WS Controller '{route.controller}' has no method '{route.action}' "
                f"for incoming action '{frame.action}'"
            )

        handler = getattr(controller, route.action)
        # expected signature:
        # async def handler(self, frame: Frame, ws: web.WebSocketResponse) -> None
        await handler(frame, ws)
        return True