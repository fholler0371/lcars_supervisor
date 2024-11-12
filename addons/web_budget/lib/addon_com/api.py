from aiohttp import web
import tomllib
import json

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.auth import Moduls
from models.basic import ListOfDict


class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
                
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        #prüfen ob einträge für allgemeine auth handler ist
        self.core.log.debug('get call')
        #auth_resp = await self._auth.handler(request, rd)
        #if auth_resp[0]:
        #    return auth_resp
        #call für dieses Modul
        self.core.log.debug(rd)
        match '/'.join(rd.path):
            case 'get_allowed_moduls':
                try:
                    rd = HttpMsgData.model_validate(rd.data)
                    rd = HttpRequestData.model_validate(rd.data)
                except:
                    pass
                data = Moduls()
                if rd.open_id and ('budget' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data.append({'mod': 'budget_overview', 'src': '/budget/js/mod/budget_overview'})
                self.core.log.debug(data)
                return (True, web.json_response(data.model_dump()))
            case 'budget/get_status':
                self.core.log.debug('Ask for Status')
                bc = rd.data.data
                if bc['open_id'] and ('budget' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    inaktiv = 'budget_sec' in bc['open_id']['app'].split(' ')
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='get_status', data={'aktiv':inaktiv}))
                    data = ListOfDict.model_validate(resp)
                    return (True, web.json_response(SendOk(data=data.model_dump()).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'user/fritzlink':
                self.core.log.debug('get fritzlinky')
                bc = rd.data.data
                if bc['open_id'] and ('router' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    return (True, web.json_response({"ok" :True, "link": self._fritzlink}))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case _:
                self.core.log.critical('/'.join(rd.path))
    
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        try:
            await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        except Exception as e:
            self.core.log.critical(repr(e))
        self.core.log.debug('Initaliesiere api done')
        
    async def _astart(self):
        self.core.log.debug('starte api')
