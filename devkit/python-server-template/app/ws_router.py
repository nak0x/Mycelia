from __future__ import annotations
from aiohttp import web
from typing import Dict, Any

from app.import_utils import import_symbol
from app.frames.frame import Frame
from app.config import AppConfig
from app.ws_controllers.base import WsController


class WsPayloadDispatcher:
    """
    Dispatch each payload item by slug to a controller/action defined in config.json.
    """

    def __init__(self, app: web.Application, cfg: AppConfig):
        self.app = app
        self.cfg = cfg
        self._controller_cache: dict[str, WsController] = {}

    def _get_controller(self, import_path: str) -> WsController:
        if import_path not in self._controller_cache:
            ControllerClass = import_symbol(import_path)
            self._controller_cache[import_path] = ControllerClass(self.app)
        return self._controller_cache[import_path]

    async def dispatch_payload(self, frame: Frame, payload: Dict[str, Any], ws: web.WebSocketResponse) -> bool:
        slug = payload.get("slug")
        if not isinstance(slug, str) or not slug:
            return False

        route = self.cfg.ws_payload_routes.get(slug)
        if route is None:
            return False

        controller = self._get_controller(route.controller)

        if not hasattr(controller, route.action):
            raise RuntimeError(f"WsController '{route.controller}' has no action '{route.action}' for slug '{slug}'")

        handler = getattr(controller, route.action)
        # Signature expected: async def handler(self, frame: Frame, payload: dict, ws: WebSocketResponse) -> None
        await handler(frame, payload, ws)
        return True