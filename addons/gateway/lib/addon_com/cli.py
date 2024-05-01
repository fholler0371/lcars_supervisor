from aiohttp import web
import time
from httplib.models import HttpHandler, HttpRequestData, HttpMsgData, SendOk

from corelib import BaseObj, Core

from models.network import Hostname


class Cli(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'auth/add_user':
                await self.core.web_l.msg_send(HttpMsgData(dest='web_auth', type='user_add', data=rd.data))
                return (True, web.json_response(SendOk.model_dump()))
        return False
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere cli')
        await self.core.web.add_handler(HttpHandler(domain = 'cli', func = self.handler, auth='local', acl='docker'))

    async def _astart(self):
        self.core.log.debug('starte cli')
