from aiohttp import web
import mimetypes
import aiofiles
import pydantic
import json

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk


TEXT_FILES = ['text/html']
class Static(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        path = '/'.join(rd.path[1:])
        if path == '':
            path = 'index.html'
        file_name = self.core.path.web / path
        if file_name.exists():
            mime = mimetypes.guess_type(file_name)[0]
            if mime in TEXT_FILES:
                async with aiofiles.open(file_name) as f:
                    content = await f.read()
                    return (True, web.Response(text=content, content_type=mime))
            
            self.core.log.debug(mime)
            self.core.log.debug(rd)
            self.core.log.debug(self.core.path.web)
            self.core.log.debug(file_name)
        return (True, web.Response(text='>>> oK <<<'))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere static')
        await self.core.web.add_handler(HttpHandler(domain = '', func = self.handler, auth='local', acl='docker'), static = True)

    async def _astart(self):
        self.core.log.debug('starte static')
