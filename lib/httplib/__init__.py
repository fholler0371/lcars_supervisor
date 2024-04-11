from aiohttp import web

from .webserver import server_start
from .local_keys import LocalKeys

from corelib import BaseObj, Core


class HTTP(BaseObj):
    def __init__(self, core: Core, sv: bool= False) -> None:
        BaseObj.__init__(self, core)
        self._sv = sv
        
    async def _handler(self, request: web.Request):
        self.core.log.debug(request.remote)
        return web.Response(text="OK")

    async def _ainit(self):
        port = 1234 if self._sv else 1235
        self.site = await server_start(port, self._handler)
        self.local_keys = LocalKeys(self.core)
        await self.local_keys._ainit()
        self.core.log.info(f'WebServer hört auf Port {port}')
    
    async def _astop(self):
        await self.site.stop()    
        self.core.log.info('WebServer gestopt')