import argparse
import asyncio
import json
import shlex
from pprint import pprint
from typing import Callable, List, Optional, Sequence, Tuple, Dict, Any


class Argument:
    def __init__(
        self,
        name: str,
        execute: Callable,
        description: str,
        arg_defs: Optional[Sequence[Tuple[Sequence[Any], Dict[str, Any]]]] = None,
    ):
        """
        Represents a console command using argparse-style parsing.

        Args:
            name: Subcommand name (e.g., "send").
            execute: Async callable executed when the command matches. Signature (args, server).
            description: Help/description shown in the console menu.
            arg_defs: Optional sequence describing parser arguments. Each entry is a tuple
                      of (*args, **kwargs) passed to parser.add_argument.
        """
        self.name = name
        self.execute = execute
        self.description = description
        self.arg_defs = arg_defs or []
        self.parser: Optional[argparse.ArgumentParser] = None

    def register(self, subparsers):
        """Register this argument on the provided subparsers object."""
        parser = subparsers.add_parser(self.name, help=self.description, add_help=False)
        parser.set_defaults(_execute=self.execute)
        for args, kwargs in self.arg_defs:
            parser.add_argument(*args, **kwargs)
        self.parser = parser
        return parser


class ConsoleLoop:
    def __init__(self, server, arguments: Optional[List[Argument]] = None):
        self.server = server
        self.arguments: List[Argument] = []
        self.parser = argparse.ArgumentParser(prog="console", add_help=False)
        self.subparsers = self.parser.add_subparsers(dest="command")
        if arguments:
            for argument in arguments:
                self.add_argument(argument)
        else:
            self._setup_default_arguments()

    def _setup_default_arguments(self):
        """Setup default command arguments (Unix-style)."""

        # quit
        self.add_argument(
            Argument(
                name="quit",
                execute=self._execute_quit,
                description="quit      -> stop server",
            )
        )

        # clients
        self.add_argument(
            Argument(
                name="clients",
                execute=self._execute_clients,
                description="clients   -> show connected client count",
            )
        )

        # send
        self.add_argument(
            Argument(
                name="send",
                execute=self._execute_send_payload,
                description="send --slug <slug> --value <value> --type <type> --target <receiver> [--debug]",
                arg_defs=[
                    (("--slug",), {"required": True, "help": "Payload slug"}),
                    (("--value",), {"required": True, "help": "Payload value"}),
                    (
                        ("--type",),
                        {
                            "required": True,
                            "dest": "datatype",
                            "help": "Payload datatype",
                        },
                    ),
                    (
                        ("--target",),
                        {
                            "required": True,
                            "dest": "receiver_id",
                            "help": "Receiver ID",
                        },
                    ),
                    (
                        ("--metadata-type",),
                        {
                            "dest": "message_type",
                            "default": "ws-data",
                            "help": "Metadata type field",
                        },
                    ),
                    (
                        ("--debug",),
                        {
                            "action": "store_true",
                            "help": "Pretty-print payload before sending",
                        },
                    ),
                ],
            )
        )

    async def _execute_quit(self, args: argparse.Namespace, server):
        """Execute quit command."""
        raise SystemExit(0)

    async def _execute_clients(self, args: argparse.Namespace, server):
        """Execute clients command."""
        async with server.clients_lock:
            print(f"Connected clients: {len(server.clients)}")

    async def _execute_send_payload(self, args: argparse.Namespace, server):
        """Execute structured send command."""
        typed_value = self._coerce_value(args.datatype, args.value)
        payload = server.build_payload_dict(
            slug=args.slug,
            value=typed_value,
            datatype=args.datatype,
            receiver_id=args.receiver_id,
            message_type=args.message_type,
        )
        if args.debug:
            print("Payload debug:")
            pprint(payload)
        msg = json.dumps(payload)
        await self._broadcast_message(msg, server)

    def _coerce_value(self, datatype: str, raw_value: str):
        """Convert string raw value to proper Python type based on datatype."""
        dtype = datatype.lower()
        if dtype in {"bool", "boolean"}:
            return raw_value.lower() in {"1", "true", "on", "yes"}
        if dtype in {"int", "integer"}:
            try:
                return int(raw_value)
            except ValueError:
                print(f"Warning: unable to parse '{raw_value}' as integer; sending as string.")
                return raw_value
        if dtype in {"float", "double"}:
            try:
                return float(raw_value)
            except ValueError:
                print(f"Warning: unable to parse '{raw_value}' as float; sending as string.")
                return raw_value
        return raw_value

    async def _broadcast_message(self, msg: str, server):
        """Broadcast a message to all connected clients."""
        async with server.clients_lock:
            clients = list(server.clients)

        if not clients:
            print("No clients connected.")
            return

        results = await asyncio.gather(*(c.send(msg) for c in clients), return_exceptions=True)
        ok = sum(1 for r in results if not isinstance(r, Exception))
        print(f"Sent to {ok}/{len(clients)} clients.")

    def add_argument(self, argument: Argument):
        """Add a custom argument to the console loop."""
        self.arguments.append(argument)
        argument.register(self.subparsers)

    async def run(self):
        """Run the console loop."""
        print("Console commands:")
        for arg in self.arguments:
            print(f"  {arg.description}")

        while True:
            cmd = (await asyncio.to_thread(input, "> ")).strip()
            if not cmd:
                continue

            try:
                args = self.parser.parse_args(shlex.split(cmd))
            except SystemExit:
                # argparse prints error; continue prompt
                continue

            execute_fn = getattr(args, "_execute", None)
            if not execute_fn:
                print("Unknown command.")
                continue

            try:
                await execute_fn(args, self.server)
            except SystemExit:
                raise
            except Exception as e:
                print(f"Error executing command: {e}")

