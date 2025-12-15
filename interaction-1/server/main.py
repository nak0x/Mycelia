import asyncio
import argparse
import threading
from ws_server import WebSocketServer


def run_server_in_thread(server: WebSocketServer, host: str, port: int,
                        ssl_enabled: bool = False, ssl_keyfile: str = None,
                        ssl_certfile: str = None, ssl_password: str = None,
                        ssl_ca_cert: str = None, ssl_certs_reqs: int = 0):
    """Run the WebSocket server in an asyncio event loop within a thread."""
    def run_async():
        try:
            asyncio.run(server.run(
                host=host,
                port=port,
                ssl_enabled=ssl_enabled,
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
                ssl_password=ssl_password,
                ssl_ca_cert=ssl_ca_cert,
                ssl_certs_reqs=ssl_certs_reqs
            ))
        except SystemExit:
            pass
        except Exception as e:
            print(f"Server error: {e}")

    thread = threading.Thread(target=run_async, daemon=True)
    thread.start()
    return thread


def main():
    parser = argparse.ArgumentParser(description="Args like --key=value")
    parser.add_argument("--ssl", action="store_true", help="Switch TLS on.")
    parser.add_argument("--ssl-keyfile", type=str, help="Server's secret key file.")
    parser.add_argument("--ssl-certfile", type=str, help="Server's certificate file.")
    parser.add_argument("--ssl-password", default=None, type=str, help="Pass phrase.")
    parser.add_argument("--ssl-ca-cert", type=str, help="CA's certificate.")
    parser.add_argument("--ssl-certs-reqs", type=int, default=0, help="Flag for certificate requires.")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")

    args = parser.parse_args()

    # Create server instance
    server = WebSocketServer()

    # Run server in a thread
    server_thread = run_server_in_thread(
        server=server,
        host=args.host,
        port=args.port,
        ssl_enabled=args.ssl,
        ssl_keyfile=args.ssl_keyfile,
        ssl_certfile=args.ssl_certfile,
        ssl_password=args.ssl_password,
        ssl_ca_cert=args.ssl_ca_cert,
        ssl_certs_reqs=args.ssl_certs_reqs
    )

    # Keep main thread alive
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    main()

