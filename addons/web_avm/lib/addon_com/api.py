from aiohttp import web

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.auth import Moduls
import aioauth

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._auth = aioauth.Client(self.core)
                
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        #prüfen ob einträge für allgemeine auth handler ist
        auth_resp = await self._auth.handler(request, rd)
        if auth_resp[0]:
            return auth_resp
        #call für dieses Modul
        match '/'.join(rd.path):
            case 'get_allowed_moduls':
                try:
                    rd = HttpMsgData.model_validate(rd.data)
                    rd = HttpRequestData.model_validate(rd.data)
                except:
                    pass
                if rd.open_id and ('avm' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = Moduls()
                    #data.append({'mod': 'auth_user', 'src': '/auth/js/mod/auth_user'})
                    return (True, web.json_response(data.model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case _:
                self.core.log.critical('/'.join(rd.path))
    
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        
    async def _astart(self):
        self.core.log.debug('starte api')
