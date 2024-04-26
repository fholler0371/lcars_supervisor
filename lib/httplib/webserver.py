from typing import Any
from aiohttp import web

async def server_start(port: int, handler: Any) -> object:
    server = web.Server(handler, access_log=None)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    return site