from aiohttp import web
from app.config import load_config
from app.server import build_app


def main() -> None:
    cfg = load_config("config.json")
    app = build_app(cfg)
    web.run_app(app, host=cfg.server.host, port=cfg.server.port)


if __name__ == "__main__":
    main()