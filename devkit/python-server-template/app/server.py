from aiohttp import web, WSMsgType

from app.config import AppConfig
from app.ws_hub import WsHub
from app.http_router import mount_routes
from app.ws_router import WsActionDispatcher
from app.frames.parser import FrameParser


async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    hub: WsHub = request.app["hub"]
    dispatcher: WsActionDispatcher = request.app["ws_dispatcher"]

    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)
    await hub.add(ws)

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue

            raw = msg.data

            # Validate + parse new frame
            try:
                frame = FrameParser(raw).parse()
            except Exception as e:
                # invalid input -> ignore (or you can reply with an error message)
                print(f"[WS] Invalid frame ignored: {e}")
                continue

            # If action is configured, call controller
            try:
                handled = await dispatcher.dispatch(frame, ws)
            except Exception as e:
                print(f"[WS] Handler error for action={frame.action}: {e}")
                handled = True  # treated as handled, but failed

            # Broadcast behavior:
            # - if you still want to broadcast everything, keep this:
            await hub.broadcast(raw)

            # OR if you want broadcast only when not handled:
            # if not handled:
            #     await hub.broadcast(raw, sender=ws)

    finally:
        await hub.remove(ws)

    return ws


def build_app(cfg: AppConfig) -> web.Application:
    app = web.Application()

    app["hub"] = WsHub(app)
    app["server_id"] = cfg.server.id
    app["ws_dispatcher"] = WsActionDispatcher(app, cfg)

    # websocket route
    app.router.add_get(cfg.server.ws_path, ws_handler)

    # http routes
    mount_routes(app, cfg)

    return app