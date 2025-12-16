#!/usr/bin/env python3
"""
ws_client.py — one-file interactive WebSocket Frame client

Install:
  pip install "websockets>=12"

Run:
  python ws_client.py --url ws://localhost:8000/ws --interactive
  python ws_client.py --url ws://localhost:8000/ws --send slug=led datatype=boolean value=true
  python ws_client.py --url ws://localhost:8000/ws --send slug=message datatype=string value="hello"

Interactive commands (type "help"):
  show
  set sender_id=... receiver_id=... frame_type=... connection_status=...
  send slug=led datatype=boolean value=true
  send slug=message datatype=string value="hello"
  send value=123 datatype=int slug=temp
  send payload='[{"slug":"x","datatype":"int","value":1}]'
  raw {"any":"json"}
  led on | led off
  quit
"""

import argparse
import asyncio
import json
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional, Protocol, runtime_checkable, List

import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI, InvalidHandshake


# ---- Minimal protocol typing ----
@runtime_checkable
class WsLike(Protocol):
    async def send(self, message: str) -> None: ...
    async def close(self) -> None: ...
    def __aiter__(self): ...


# ---------------- Frame helpers ----------------
def _now_message_id() -> str:
    return f"MSG-{datetime.now().isoformat()}-{uuid.uuid4().hex[:6]}"


def build_frame(
    sender_id: str,
    receiver_id: str,
    frame_type: str,
    payload: List[Dict[str, Any]],
    connection_status: int = 200,
    message_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "metadata": {
            "senderId": sender_id,
            "timestamp": time.time(),
            "messageId": message_id or _now_message_id(),
            "type": frame_type,
            "receiverId": receiver_id,
            "status": {"connection": connection_status},
        },
        "payload": payload,
    }


def _normalize_bool(s: str) -> bool:
    s = s.strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    raise ValueError(f"Invalid boolean value: {s}")


def coerce_value(datatype: str, raw: Any) -> Any:
    """
    Convertit raw -> type selon datatype.
    datatype supportés (pragmatique) :
      boolean, bool, string, str, int, integer, float, number, json, object
    """
    dt = (datatype or "").strip().lower()

    # Si on reçoit déjà un objet python, on ne force pas trop
    if not isinstance(raw, str):
        if dt in ("boolean", "bool") and isinstance(raw, bool):
            return raw
        if dt in ("int", "integer") and isinstance(raw, int):
            return raw
        if dt in ("float", "number") and isinstance(raw, (int, float)):
            return float(raw) if dt in ("float", "number") else raw
        if dt in ("json", "object") and isinstance(raw, (dict, list)):
            return raw
        if dt in ("string", "str"):
            return str(raw)
        # fallback
        return raw

    s = raw.strip()

    if dt in ("boolean", "bool"):
        return _normalize_bool(s)

    if dt in ("int", "integer"):
        return int(s)

    if dt in ("float", "number"):
        return float(s)

    if dt in ("json", "object"):
        # accepte dict/list JSON
        return json.loads(s)

    # string
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


async def send_json(ws: WsLike, obj: Dict[str, Any]) -> None:
    raw = json.dumps(obj, ensure_ascii=False)
    await ws.send(raw)
    print(f"> {raw}")


async def listen_loop(ws: WsLike) -> None:
    async for msg in ws:
        print(f"\n< {msg}")
        try:
            obj = json.loads(msg)
            print(json.dumps(obj, indent=2, ensure_ascii=False))
        except Exception:
            pass


# ---------------- CLI parsing utils ----------------
def parse_kv_tokens(tokens: List[str]) -> Dict[str, str]:
    """
    Parse une liste du style:
      ["slug=led", "datatype=boolean", "value=true"]
    ou un seul token 'payload=...'
    """
    out: Dict[str, str] = {}
    for t in tokens:
        if "=" not in t:
            raise ValueError(f"Expected key=value, got: {t}")
        k, v = t.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def parse_send_args(kv: Dict[str, str]) -> Dict[str, Any]:
    """
    Autorise:
      send slug=... datatype=... value=...
    ou:
      send payload='[...]'  (payload JSON complet)
    """
    if "payload" in kv:
        payload_obj = json.loads(kv["payload"])
        if not isinstance(payload_obj, list):
            raise ValueError("payload must be a JSON array (list).")
        return {"payload": payload_obj}

    slug = kv.get("slug", "message")
    datatype = kv.get("datatype", "string")
    if "value" not in kv:
        raise ValueError("Missing value=... (or payload=...)")

    value = coerce_value(datatype, kv["value"])
    return {"payload": [{"slug": slug, "datatype": datatype, "value": value}]}


# ---------------- Interactive state ----------------
@dataclass
class Defaults:
    sender_id: str = "CLIENT-ONEFILE"
    receiver_id: str = "SERVER"
    frame_type: str = "ws-data"
    connection_status: int = 200

    def to_pretty(self) -> str:
        d = asdict(self)
        return json.dumps(d, indent=2, ensure_ascii=False)


HELP_TEXT = """
Commands:
  help
  show
  set sender_id=... receiver_id=... frame_type=... connection_status=...

  send slug=<slug> datatype=<datatype> value=<value>
      Examples:
        send slug=led datatype=boolean value=true
        send slug=message datatype=string value="hello"
        send slug=temp datatype=int value=42
        send slug=pi datatype=float value=3.14
        send slug=meta datatype=json value='{"a":1,"b":2}'

  send payload='<JSON array payload>'
      Example:
        send payload='[{"slug":"led","datatype":"boolean","value":true},{"slug":"x","datatype":"int","value":1}]'

  raw <json>
      Sends the JSON as-is (no Frame wrapping).
      Example:
        raw {"hello":"world"}

  led on | led off
  quit
""".strip()


async def interactive_send_loop(ws: WsLike, defaults: Defaults) -> None:
    print("\nInteractive mode (type 'help')")

    while True:
        line = (await asyncio.to_thread(input, "> ")).strip()
        if not line:
            continue

        if line in ("quit", "exit"):
            return

        if line == "help":
            print(HELP_TEXT)
            continue

        if line == "show":
            print(defaults.to_pretty())
            continue

        if line.startswith("set "):
            try:
                kv = parse_kv_tokens(line.split()[1:])
                for k, v in kv.items():
                    if k == "sender_id":
                        defaults.sender_id = v
                    elif k == "receiver_id":
                        defaults.receiver_id = v
                    elif k == "frame_type":
                        defaults.frame_type = v
                    elif k == "connection_status":
                        defaults.connection_status = int(v)
                    else:
                        print(f"Unknown default key: {k}")
                print("OK. Current defaults:")
                print(defaults.to_pretty())
            except Exception as e:
                print(f"Error: {e}")
            continue

        if line == "led on":
            frame = build_frame(
                defaults.sender_id,
                defaults.receiver_id,
                defaults.frame_type,
                payload=[{"datatype": "boolean", "value": True, "slug": "led"}],
                connection_status=defaults.connection_status,
            )
            await send_json(ws, frame)
            continue

        if line == "led off":
            frame = build_frame(
                defaults.sender_id,
                defaults.receiver_id,
                defaults.frame_type,
                payload=[{"datatype": "boolean", "value": False, "slug": "led"}],
                connection_status=defaults.connection_status,
            )
            await send_json(ws, frame)
            continue

        if line.startswith("raw "):
            raw = line[4:].strip()
            try:
                obj = json.loads(raw)  # validate only
                await ws.send(json.dumps(obj, ensure_ascii=False))
                print(f"> {raw}")
            except Exception as e:
                print(f"Error: {e}")
            continue

        if line.startswith("send "):
            try:
                kv = parse_kv_tokens(line.split()[1:])
                send_spec = parse_send_args(kv)
                payload = send_spec["payload"]

                frame = build_frame(
                    defaults.sender_id,
                    defaults.receiver_id,
                    defaults.frame_type,
                    payload=payload,
                    connection_status=defaults.connection_status,
                )
                await send_json(ws, frame)
            except Exception as e:
                print(f"Error: {e}")
            continue

        print("Unknown command. Type 'help'.")


# ---------------- Main run loop with reconnect ----------------
async def run_client(
    url: str,
    defaults: Defaults,
    send_once: Optional[Dict[str, Any]],
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

                if send_once is not None:
                    frame = build_frame(
                        defaults.sender_id,
                        defaults.receiver_id,
                        defaults.frame_type,
                        payload=send_once["payload"],
                        connection_status=defaults.connection_status,
                    )
                    await send_json(ws, frame)

                if interactive:
                    await interactive_send_loop(ws, defaults)
                    await ws.close()

                await listener_task

        except (ConnectionClosed, OSError, InvalidURI, InvalidHandshake) as e:
            print(f"Disconnected: {e}")

        print(f"Reconnecting in {delay:.1f}s ...")
        await asyncio.sleep(delay)
        delay = min(reconnect_max, delay * 1.8)


def main() -> None:
    p = argparse.ArgumentParser(description="One-file WS interactive Frame client with defaults + reconnect")
    p.add_argument("--url", default="ws://localhost:8000/ws", help="WebSocket URL")

    # defaults (can still be changed in interactive mode)
    p.add_argument("--sender-id", default="CLIENT-ONEFILE", help="Default metadata.senderId")
    p.add_argument("--receiver-id", default="SERVER", help="Default metadata.receiverId")
    p.add_argument("--frame-type", default="ws-data", help="Default metadata.type")
    p.add_argument("--connection-status", type=int, default=200, help="Default metadata.status.connection")

    # one-shot send
    p.add_argument(
        "--send",
        nargs="*",
        default=None,
        help='Send once on connect. Use: slug=... datatype=... value=...  OR  payload=\'[...]\'',
    )

    p.add_argument("--interactive", action="store_true", help="Interactive mode")
    p.add_argument("--ping-interval", type=int, default=20, help="Ping interval (seconds)")
    p.add_argument("--reconnect-min", type=float, default=1.0, help="Min reconnect delay (seconds)")
    p.add_argument("--reconnect-max", type=float, default=20.0, help="Max reconnect delay (seconds)")
    args = p.parse_args()

    defaults = Defaults(
        sender_id=args.sender_id,
        receiver_id=args.receiver_id,
        frame_type=args.frame_type,
        connection_status=args.connection_status,
    )

    send_once = None
    if args.send is not None:
        # If user passed --send without params, argparse gives [] ; treat as error.
        if len(args.send) == 0:
            raise SystemExit("--send requires key=value tokens (or omit --send).")
        kv = parse_kv_tokens(args.send)
        send_once = parse_send_args(kv)

    asyncio.run(
        run_client(
            url=args.url,
            defaults=defaults,
            send_once=send_once,
            interactive=args.interactive,
            ping_interval=args.ping_interval,
            reconnect_min=args.reconnect_min,
            reconnect_max=args.reconnect_max,
        )
    )


if __name__ == "__main__":
    main()