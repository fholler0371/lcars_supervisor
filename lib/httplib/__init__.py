from aiohttp import web

from .webserver import server_start
from .local_keys import LocalKeys
from .client_local import ClientLocal

from corelib import BaseObj, Core


class HTTP(BaseObj):
    def __init__(self, core: Core, sv: bool= False) -> None:
        BaseObj.__init__(self, core)
        self._sv = sv
        self._handlers = []
        
    async def add_handler(self, path: str, handler: any) -> None:
        self.core.log.debug(f'Registrier Handler für: {path}')
        self._handlers.append({'path': path, 'handler': handler})

        
    async def _handler(self, request: web.Request):
        self.core.log.debug(f'{request.remote} {request.method} {request.path}')
        for entry in self._handlers:
            if str(request.path).startswith(entry['path']):
                if resp := await entry['handler'](request):
                    return resp[1]
        else:
            return web.Response(text="OK")

    async def _ainit(self):
        try:
            port = 1234 if self._sv else 1235
            self.site = await server_start(port, self._handler)
            self.local_keys = LocalKeys(self.core)
            await self.local_keys._ainit()
            self.core.log.info(f'WebServer hört auf Port {port}')
        except Exception as e:
            self.core.running.set()
            self.core.log.error(e)
    
    async def _astop(self):
        self.core.log.info('WebServer gestopt')