from aiohttp import web
from app.config import AppConfig
from app.import_utils import import_symbol
from app.controllers.base import BaseController


def mount_routes(app: web.Application, cfg: AppConfig) -> None:
    """
    Config-driven routing:
      - imports controller class
      - instantiates it once (singleton per class)
      - binds HTTP routes to controller methods
    """
    controller_cache: dict[str, BaseController] = {}

    for r in cfg.routes:
        ControllerClass = import_symbol(r.controller)

        if r.controller not in controller_cache:
            controller_cache[r.controller] = ControllerClass(app)

        controller = controller_cache[r.controller]

        if not hasattr(controller, r.action):
            raise RuntimeError(f"Controller '{r.controller}' has no action '{r.action}'")

        handler = getattr(controller, r.action)

        if r.method == "GET":
            app.router.add_get(r.path, handler)
        elif r.method == "POST":
            app.router.add_post(r.path, handler)
        elif r.method == "PUT":
            app.router.add_put(r.path, handler)
        elif r.method == "DELETE":
            app.router.add_delete(r.path, handler)
        else:
            raise ValueError(f"Unsupported method in config: {r.method}")