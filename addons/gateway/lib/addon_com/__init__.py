from aiohttp import web

from corelib import BaseObj, Core
from httplib.data import HttpHandler, HttpRequestData


class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'network/hostname':
                if self.core.web_l._hostname:
                    return (True, web.json_response({'hostname': self.core.web_l._hostname}))
                print('hostname is missing')
                resp = await self.core.web_l.get('network/hostname', dest='parent')
                if resp is not None:
                    self.core.web_l._hostname = resp.get('hostname')
                if self.core.web_l._hostname:
                    return (True, web.json_response({'hostname': self.core.web_l._hostname}))
        return False
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='docker'))
        pass
        #await self.core.web.add_handler(HttpHandler(domain = 'cli', func = self.handler, auth='local'))

    async def _astart(self):
        self.core.log.debug('starte com')
