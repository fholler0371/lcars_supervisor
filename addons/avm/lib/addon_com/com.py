from aiohttp import web
from corelib import BaseObj, Core

from httplib.models import HttpMsgData, HttpHandler, HttpRequestData

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        if rd.path[0] == 'messages':
            msg = HttpMsgData.model_validate(rd.data)
            if rd.path[1] == 'relay':
                relay_rd = HttpRequestData.model_validate(msg.data)
                if relay_rd.path[0] == 'dyndns':
                    self.core.log.info(relay_rd.data)
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='lcars_docker'))

    async def register_web_app(self)->None:
        self.core.log.debug('do register')
        await self.core.call_random(300, self.register_web_app)
        data = HttpHandler(domain='avm', acl='home', 
                           remote=f'{await self.core.web_l.hostname}.{self.core.const.app}')
        try:
            await self.core.web_l.msg_send(HttpMsgData(dest='web_base', type='register_web_app', data=data))
        except Exception as e:
            print(e, flush=True)
        
    async def _astart(self):
        self.core.log.debug('starte com')
        await self.core.call_random(10, self.register_web_app)
