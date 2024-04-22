from aiohttp import web
import pydantic
import json

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.data import HttpHandler, HttpRequestData

class xx(pydantic.BaseModel):
    pass

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'messages/register_web_app':
                if isinstance(rd.data, str):
                    rd.data = json.loads(rd.data)
                await self.core.web.add_handler(HttpHandler(**rd.data))
                return (True, web.json_response({}))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='docker'))
        pass
        #await self.core.web.add_handler(HttpHandler(domain = 'cli', func = self.handler, auth='local'))

    async def _astart(self):
        self.core.log.debug('starte com')
