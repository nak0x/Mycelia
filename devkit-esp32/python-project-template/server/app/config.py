import json
from dataclasses import dataclass
from typing import List


@dataclass
class ServerConfig:
    host: str
    port: int
    ws_path: str


@dataclass
class RouteConfig:
    method: str
    path: str
    controller: str   # import path: "app.controllers.sample.SampleController"
    action: str       # method name on the controller instance


@dataclass
class AppConfig:
    server: ServerConfig
    routes: List[RouteConfig]


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    s = raw.get("server", {})
    routes = raw.get("routes", [])

    return AppConfig(
        server=ServerConfig(
            host=s.get("host", "0.0.0.0"),
            port=int(s.get("port", 8000)),
            ws_path=s.get("ws_path", "/ws"),
        ),
        routes=[
            RouteConfig(
                method=r["method"].upper(),
                path=r["path"],
                controller=r["controller"],
                action=r["action"],
            )
            for r in routes
        ],
    )