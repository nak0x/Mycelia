#!/usr/bin/env python3
"""
ws_client.py — one-file interactive WebSocket Semantic-Action client (NEW frame format)

Frame format sent/received:
{
  "metadata": {
    "timestamp": 1678886400,
    "senderId": "ESP32-010101"
  },
  "action": "ping",
  "value": null
}

Install:
  pip install "websockets>=12"

Run:
  python ws_client.py --url ws://localhost:8000/ws --interactive
  python ws_client.py --url ws://localhost:8000/ws --send action=ping value=null
  python ws_client.py --url ws://localhost:8000/ws --send action=led value=true
  python ws_client.py --url ws://localhost:8000/ws --send action=set_temp value=21

Interactive commands (type "help"):
  show
  set sender_id=...
  send action=<action> value=<value>
  raw {"any":"json"}
  ping
  led on | led off
  quit
"""

import argparse
import asyncio
import json
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Protocol, runtime_checkable, List

import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI, InvalidHandshake


# ---- Minimal protocol typing ----
@runtime_checkable
class WsLike(Protocol):
    async def send(self, message: str) -> None: ...
    async def close(self) -> None: ...
    def __aiter__(self): ...


# ---------------- Frame helpers (NEW FORMAT) ----------------
def build_frame(sender_id: str, action: str, value: Any) -> Dict[str, Any]:
    return {
        "metadata": {
            "timestamp": time.time(),
            "senderId": sender_id,
        },
        "action": action,
        "value": value,
    }


def parse_literal_value(raw: str) -> Any:
    """
    Parses a user-provided value string into Python types.

    Supported:
      - null / none        -> None
      - true / false       -> bool
      - numbers            -> int/float
      - quoted strings     -> str (keeps inner)
      - JSON objects/arrays -> dict/list
      - fallback           -> raw string
    """
    s = raw.strip()

    if s.lower() in ("null", "none"):
        return None
    if s.lower() in ("true", "false"):
        return s.lower() == "true"

    # JSON object/array
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        return json.loads(s)

    # quoted string
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]

    # number
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        pass

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
    Parse tokens like:
      ["action=ping", "value=null"]
      ["action=set_temp", "value=21"]
      ["action=meta", "value={\"a\":1}"]
    """
    out: Dict[str, str] = {}
    for t in tokens:
        if "=" not in t:
            raise ValueError(f"Expected key=value, got: {t}")
        k, v = t.split("=", 1)
        out[k.strip()] = v.strip()
    return out


# ---------------- Interactive state ----------------
@dataclass
class Defaults:
    sender_id: str = "CLIENT-ONEFILE"

    def to_pretty(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


HELP_TEXT = """
Commands:
  help
  show
  set sender_id=...

  send action=<action> value=<value>
      Examples:
        send action=ping value=null
        send action=led value=true
        send action=set_temp value=21
        send action=set_name value="kitchen"
        send action=set_meta value='{"a":1,"b":2}'

  raw <json>
      Sends the JSON as-is (no Frame wrapping).
      Example:
        raw {"metadata":{"timestamp":1,"senderId":"X"},"action":"ping","value":null}

  ping
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
                    else:
                        print(f"Unknown default key: {k}")
                print("OK. Current defaults:")
                print(defaults.to_pretty())
            except Exception as e:
                print(f"Error: {e}")
            continue

        if line == "ping":
            frame = build_frame(defaults.sender_id, "ping", None)
            await send_json(ws, frame)
            continue

        if line == "led on":
            frame = build_frame(defaults.sender_id, "led", True)
            await send_json(ws, frame)
            continue

        if line == "led off":
            frame = build_frame(defaults.sender_id, "led", False)
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
                if "action" not in kv:
                    raise ValueError("Missing action=...")

                action = kv["action"]
                value_raw = kv.get("value", "null")
                value = parse_literal_value(value_raw)

                frame = build_frame(defaults.sender_id, action, value)
                await send_json(ws, frame)
            except Exception as e:
                print(f"Error: {e}")
            continue

        print("Unknown command. Type 'help'.")


# ---------------- Main run loop with reconnect ----------------
async def run_client(
    url: str,
    defaults: Defaults,
    send_once: Optional[Dict[str, str]],
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
                    action = send_once.get("action")
                    if not action:
                        raise ValueError("--send requires action=...")

                    value_raw = send_once.get("value", "null")
                    value = parse_literal_value(value_raw)

                    frame = build_frame(defaults.sender_id, action, value)
                    await send_json(ws, frame)

                if interactive:
                    await interactive_send_loop(ws, defaults)
                    await ws.close()

                await listener_task

        except (ConnectionClosed, OSError, InvalidURI, InvalidHandshake) as e:
            print(f"Disconnected: {e}")
        except Exception as e:
            print(f"Error: {e}")

        print(f"Reconnecting in {delay:.1f}s ...")
        await asyncio.sleep(delay)
        delay = min(reconnect_max, delay * 1.8)


def main() -> None:
    p = argparse.ArgumentParser(description="One-file WS semantic-action client (new frame format) with reconnect")
    p.add_argument("--url", default="ws://localhost:8000/ws", help="WebSocket URL")
    p.add_argument("--sender-id", default="CLIENT-ONEFILE", help="Default metadata.senderId")

    # one-shot send
    p.add_argument(
        "--send",
        nargs="*",
        default=None,
        help='Send once on connect. Use: action=... value=... (value can be null/true/false/number/"string"/JSON)',
    )

    p.add_argument("--interactive", action="store_true", help="Interactive mode")
    p.add_argument("--ping-interval", type=int, default=20, help="Ping interval (seconds)")
    p.add_argument("--reconnect-min", type=float, default=1.0, help="Min reconnect delay (seconds)")
    p.add_argument("--reconnect-max", type=float, default=20.0, help="Max reconnect delay (seconds)")
    args = p.parse_args()

    defaults = Defaults(sender_id=args.sender_id)

    send_once = None
    if args.send is not None:
        if len(args.send) == 0:
            raise SystemExit("--send requires key=value tokens (or omit --send).")
        send_once = parse_kv_tokens(args.send)

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