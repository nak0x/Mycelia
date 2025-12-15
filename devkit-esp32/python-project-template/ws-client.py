#!/usr/bin/env python3
"""
ws_client.py — one-file WebSocket client (keeps connection, sends a Frame, prints incoming frames)

Install:
  pip install "websockets>=12"

Run:
  python ws_client.py --url ws://localhost:8000/ws
  python ws_client.py --url ws://localhost:8000/ws --send-led true
  python ws_client.py --url ws://localhost:8000/ws --send-text "hello"
  python ws_client.py --interactive
"""

import argparse
import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Protocol, runtime_checkable

import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI, InvalidHandshake


# ---- Minimal protocol typing (no deprecated class) ----
@runtime_checkable
class WsLike(Protocol):
    async def send(self, message: str) -> None: ...
    async def close(self) -> None: ...
    def __aiter__(self): ...


def build_frame(
    sender_id: str,
    receiver_id: str,
    frame_type: str,
    payload: list[dict[str, Any]],
    connection_status: int = 200,
    message_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "metadata": {
            "senderId": sender_id,
            "timestamp": time.time(),
            "messageId": message_id or f"MSG-{datetime.now().isoformat()}-{uuid.uuid4().hex[:6]}",
            "type": frame_type,
            "receiverId": receiver_id,
            "status": {"connection": connection_status},
        },
        "payload": payload,
    }


def parse_bool(s: str) -> bool:
    s = s.strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    raise ValueError(f"Invalid boolean value: {s}")


async def listen_loop(ws: WsLike) -> None:
    async for msg in ws:
        print(f"\n< {msg}")
        try:
            obj = json.loads(msg)
            print(json.dumps(obj, indent=2, ensure_ascii=False))
        except Exception:
            pass


async def send_frame(ws: WsLike, frame: Dict[str, Any]) -> None:
    raw = json.dumps(frame, ensure_ascii=False)
    await ws.send(raw)
    print(f"> {raw}")


async def interactive_send_loop(ws: WsLike, sender_id: str, receiver_id: str) -> None:
    print("\nInteractive mode:")
    print("  led on|off")
    print("  send <text>")
    print("  raw <json>")
    print("  quit")

    while True:
        cmd = (await asyncio.to_thread(input, "> ")).strip()
        if not cmd:
            continue

        if cmd == "quit":
            return

        try:
            if cmd == "led on":
                frame = build_frame(
                    sender_id, receiver_id, "ws-data",
                    payload=[{"datatype": "boolean", "value": True, "slug": "led"}],
                )
                await send_frame(ws, frame)

            elif cmd == "led off":
                frame = build_frame(
                    sender_id, receiver_id, "ws-data",
                    payload=[{"datatype": "boolean", "value": False, "slug": "led"}],
                )
                await send_frame(ws, frame)

            elif cmd.startswith("send "):
                text = cmd[5:]
                frame = build_frame(
                    sender_id, receiver_id, "ws-data",
                    payload=[{"datatype": "string", "value": text, "slug": "message"}],
                )
                await send_frame(ws, frame)

            elif cmd.startswith("raw "):
                raw = cmd[4:]
                obj = json.loads(raw)  # just validate json; server validates Frame
                await ws.send(json.dumps(obj, ensure_ascii=False))
                print(f"> {raw}")

            else:
                print("Unknown command.")
        except Exception as e:
            print(f"Error: {e}")


async def run_client(
    url: str,
    sender_id: str,
    receiver_id: str,
    send_text: Optional[str],
    send_led: Optional[bool],
    interactive: bool,
    ping_interval: int,
    reconnect_min: float,
    reconnect_max: float,
) -> None:
    delay = reconnect_min

    while True:
        try:
            print(f"Connecting to {url} ...")
            async with websockets.connect(
                url,
                ping_interval=ping_interval,
                ping_timeout=max(5, ping_interval),
                close_timeout=5,
                max_size=2**20,
            ) as ws:
                print("Connected ✅")
                delay = reconnect_min

                listener_task = asyncio.create_task(listen_loop(ws))

                if send_led is not None:
                    frame = build_frame(
                        sender_id, receiver_id, "ws-data",
                        payload=[{"datatype": "boolean", "value": bool(send_led), "slug": "led"}],
                    )
                    await send_frame(ws, frame)

                if send_text is not None:
                    frame = build_frame(
                        sender_id, receiver_id, "ws-data",
                        payload=[{"datatype": "string", "value": send_text, "slug": "message"}],
                    )
                    await send_frame(ws, frame)

                if interactive:
                    await interactive_send_loop(ws, sender_id, receiver_id)
                    await ws.close()

                await listener_task

        except (ConnectionClosed, OSError, InvalidURI, InvalidHandshake) as e:
            print(f"Disconnected: {e}")

        print(f"Reconnecting in {delay:.1f}s ...")
        await asyncio.sleep(delay)
        delay = min(reconnect_max, delay * 1.8)


def main() -> None:
    p = argparse.ArgumentParser(description="One-file WS Frame client with reconnect + listener")
    p.add_argument("--url", default="ws://localhost:8000/ws", help="WebSocket URL")
    p.add_argument("--sender-id", default="CLIENT-ONEFILE", help="metadata.senderId")
    p.add_argument("--receiver-id", default="SERVER", help="metadata.receiverId")
    p.add_argument("--send-text", default=None, help="Send a string frame once on connect")
    p.add_argument("--send-led", default=None, help="Send led frame once on connect: true/false")
    p.add_argument("--interactive", action="store_true", help="Interactive mode (type commands)")
    p.add_argument("--ping-interval", type=int, default=20, help="Ping interval in seconds")
    p.add_argument("--reconnect-min", type=float, default=1.0, help="Min reconnect delay")
    p.add_argument("--reconnect-max", type=float, default=20.0, help="Max reconnect delay")
    args = p.parse_args()

    send_led = None
    if args.send_led is not None:
        send_led = parse_bool(args.send_led)

    asyncio.run(
        run_client(
            url=args.url,
            sender_id=args.sender_id,
            receiver_id=args.receiver_id,
            send_text=args.send_text,
            send_led=send_led,
            interactive=args.interactive,
            ping_interval=args.ping_interval,
            reconnect_min=args.reconnect_min,
            reconnect_max=args.reconnect_max,
        )
    )


if __name__ == "__main__":
    main()