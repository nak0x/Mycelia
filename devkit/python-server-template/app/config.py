import json
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ServerConfig:
    id: str
    host: str
    port: int
    ws_path: str


@dataclass
class RouteConfig:
    method: str
    path: str
    controller: str
    action: str

@dataclass
class WsPayloadRouteConfig:
    controller: str
    action: str

@dataclass
class AppConfig:
    server: ServerConfig
    routes: List[RouteConfig]
    ws_payload_routes: Dict[str, WsPayloadRouteConfig]


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    s = raw.get("server", {})
    routes = raw.get("routes", [])
    ws_payload_routes_raw = raw.get("ws_payload_routes", {})

    ws_payload_routes = {
        slug: WsPayloadRouteConfig(
            controller=cfg["controller"],
            action=cfg["action"]
        )
        for slug, cfg in ws_payload_routes_raw.items()
    }

    return AppConfig(
        server=ServerConfig(
            id=s.get("id", "SERVER-000000"),
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
        ws_payload_routes=ws_payload_routes
    )