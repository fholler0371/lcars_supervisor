from aiohttp import web
import pydantic
import json

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk


class Static(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        self.core.log.debug(rd)
        return (True, web.Response(text='Hello World'))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere static')
        await self.core.web.add_handler(HttpHandler(domain = '', func = self.handler, auth='local', acl='docker'), static = True)

    async def _astart(self):
        self.core.log.debug('starte static')
