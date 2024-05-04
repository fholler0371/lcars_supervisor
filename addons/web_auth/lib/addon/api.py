from aiohttp import web
import json

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from addon.models import UserLogin

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._acl = None
        
    async def check_ip(self, ip: str) -> None:
        try:
         if self._acl is None:
            await self.core.web_l.msg_send(HttpMsgData(dest='avm', type='get_ip'))
            pass
        except Exception as e:
            self.core.log.error(e)
        
        
    async def doLogin(self, rd:HttpRequestData, ldata: UserLogin) -> tuple:
        self.core.log.debug(await self.check_ip(ldata.ip))
        self.core.log.debug(ldata)
             
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'do_login':
                msg = HttpMsgData.model_validate(rd.data)
                msg2 = HttpRequestData.model_validate(msg.data)
                ldata = UserLogin.model_validate_json(msg2.data)
                ldata.ip = msg2.ip
                await self.doLogin(rd, ldata)
                                     
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
 
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(10, self.register_web_app)
