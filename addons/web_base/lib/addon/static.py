from aiohttp import web
import mimetypes
import aiofiles
import pydantic
import json

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk


TEXT_FILES = ['text/html', 'text/javascript', 'text/css']
SVG_FILES = ['image/svg+xml']
BIN_FILES = ['font/ttf', 'image/png']
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
                    return (True, web.Response(text=await f.read(), content_type=mime))
            elif mime in SVG_FILES:
                async with aiofiles.open(file_name) as f:
                    content = await f.read()
                    content = content.replace('<path', '<path fill="currentColor" stroke="currentColor"')
                    return (True, web.Response(text=content, content_type=mime))
            elif mime in BIN_FILES:
                async with aiofiles.open(file_name, 'br') as f:
                    return (True, web.Response(body=await f.read(), content_type=mime))
            
            #self.core.log.debug(mime)
            #self.core.log.debug(rd)
            #self.core.log.debug(self.core.path.web)
            #self.core.log.debug(file_name)
        return (True, web.Response(status=404, text='>>> oK <<<'))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere static')
        await self.core.web.add_handler(HttpHandler(domain = '', func = self.handler, auth='local', acl='docker'), static = True)

    async def _astart(self):
        self.core.log.debug('starte static')
