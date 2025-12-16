from aiohttp import web, WSMsgType
from app.config import AppConfig
from app.ws_hub import WsHub
from app.http_router import mount_routes
from app.frames.parser import FrameParser
from app.frames.factory import error_frame_json
from app.ws_router import WsPayloadDispatcher

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

                # validate + parse
                try:
                    parser = FrameParser(raw)
                    frame = parser.parse()
                except Exception as e:
                    await ws.send_str(error_frame_json(
                        sender=request.app["server_id"],
                        receiver="UNKNOWN",
                        message=f"Invalid frame: {e}",
                        connection_status=400
                    ))
                    continue

                # If the frame targets THIS server: dispatch each payload by slug
                if frame.metadata.get("receiverId") == request.app["server_id"]:
                    dispatcher = request.app["ws_payload_dispatcher"]

                    # Call handler for each payload
                    for payload in frame.payloads:
                        await dispatcher.dispatch_payload(frame, payload, ws)

                # Rebroadcast original frame to other clients
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
    app["server_id"] = cfg.server.id
    app["ws_payload_dispatcher"] = WsPayloadDispatcher(app, cfg)

    # websocket route
    app.router.add_get(cfg.server.ws_path, ws_handler)

    # http routes from config.json (controllers)
    mount_routes(app, cfg)

    return app