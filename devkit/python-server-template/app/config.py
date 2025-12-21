import json
from dataclasses import dataclass
from typing import Dict, List


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
class WsActionConfig:
    controller: str
    action: str


@dataclass
class AppConfig:
    server: ServerConfig
    routes: List[RouteConfig]
    ws_actions: Dict[str, WsActionConfig]


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    s = raw.get("server", {})
    routes_raw = raw.get("routes", [])
    ws_actions_raw = raw.get("ws_actions", {})

    return AppConfig(
        server=ServerConfig(
            id=s.get("id", "SERVER"),
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
            for r in routes_raw
        ],
        ws_actions={
            action_name: WsActionConfig(
                controller=cfg["controller"],
                action=cfg["action"]
            )
            for action_name, cfg in ws_actions_raw.items()
        }
    )