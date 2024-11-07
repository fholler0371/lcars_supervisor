from aiohttp import web
import tomllib
import json

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.auth import Moduls
from models.network import IpData
import aioauth


class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._fritzlink = ''
        self._auth = aioauth.Client(self.core)
        with open("/lcars/config/config.toml", "rb") as f:
            config = tomllib.load(f)
            self.core.log.debug(config.get('avm', {}).get('fritzlimk', ''))
            self._fritzlink = config.get('avm', {}).get('fritzlimk', '')
            self.core.log.debug(self._fritzlink)
                
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
                if rd.open_id and ('router' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = Moduls()
                    data.append({'mod': 'router_net', 'src': '/router/js/mod/router_net'})
                    return (True, web.json_response(data.model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'user/get_record':
                self.core.log.debug('Ask for route')
                bc = rd.data.data
                if bc['open_id'] and ('router' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='avm', type='get_all_ip'))
                    data = IpData.model_validate(resp)
                    self.core.log.debug(data)
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
        await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        with open("/lcars/config/config.toml", "rb") as f:
            config = tomllib.load(f)
            self._fritzlink = config.get('avm', {}).get('fritzlink', '')
        
    async def _astart(self):
        self.core.log.debug('starte api')
