from aiohttp import web
from corelib import BaseObj, Core
import json

from httplib.data import HttpMsgData, HttpHandler, HttpRequestData

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        self.core.log.info('/'.join(rd.path))
        self.core.log.info(rd.data)
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='lcars_docker'))

    async def register_web_app(self)->None:
        self.core.log.debug('do register')
        await self.core.call_random(300, self.register_web_app)
        data = HttpHandler(domain='avm', acl='home', 
                           remote=f'{await self.core.web_l.hostname}.{self.core.const.app}')
        msg = HttpMsgData(dest='web_base', type='register_web_app', 
                          data=data.model_dump_json())
        try:
            await self.core.web_l.msg_send(msg)
        except Exception as e:
            print(e, flush=True)
        
    async def _astart(self):
        self.core.log.debug('starte com')
        await self.core.call_random(10, self.register_web_app)
