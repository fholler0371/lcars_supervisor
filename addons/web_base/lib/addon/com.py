from aiohttp import web
import pydantic
import json

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk


class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'messages/register_web_app':
                msg = rd.data
                data = HttpHandler.model_validate(msg.data)
                await self.core.web.add_handler(data)
                return (True, web.json_response(SendOk().model_dump()))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='docker'))

    async def _astart(self):
        self.core.log.debug('starte com')
