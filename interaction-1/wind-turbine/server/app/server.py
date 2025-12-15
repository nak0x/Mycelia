from aiohttp import web, WSMsgType
from app.config import AppConfig
from app.ws_hub import WsHub
from app.router import mount_routes
from app.frames.parser import FrameParser
from app.frames.factory import error_frame_json


async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    hub: WsHub = request.app["hub"]
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)

    await hub.add(ws)
    print("New WS client.")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                raw = msg.data

                # Validate incoming WS message as a Frame
                try:
                    FrameParser(raw)  # validate only
                except Exception as e:
                    # Send error frame back to sender (and do not rebroadcast)
                    await ws.send_str(error_frame_json(
                        sender="SERVER",
                        receiver="UNKNOWN",
                        message=f"Invalid frame: {e}",
                        connection_status=400
                    ))
                    continue

                # Rebroadcast valid frames to other clients
                await hub.broadcast(raw, sender=ws)

            elif msg.type == WSMsgType.ERROR:
                print("WS error:", ws.exception())
                break
    finally:
        await hub.remove(ws)
        print("WS client disconnected.")

    return ws


def build_app(cfg: AppConfig) -> web.Application:
    app = web.Application()

    # shared hub
    app["hub"] = WsHub()

    # websocket route
    app.router.add_get(cfg.server.ws_path, ws_handler)

    # http routes from config.json (controllers)
    mount_routes(app, cfg)

    return app