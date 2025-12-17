from aiohttp import web

class HTTPServer:
    def __init__(self, port, routes=None):
        self.port = port
        self.app = web.Application()
        if routes:
            self.app.add_routes(routes)
        self.runner = None
        self.site = None

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await self.site.start()
        print(f"🌐 Serveur HTTP démarré sur http://0.0.0.0:{self.port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
