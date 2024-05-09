from aiohttp import web
import time
import json

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, HttpMsgData, SendOk
from models.auth import Moduls
import aioauth

#from addon.models import Moduls
from  addon.models import Apps

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._auth = aioauth.Client(self.core)
        self._apps = {}
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        #Umleiten von api calls
        for entry in self.core.web._handlers:
            if entry.remote and entry.domain == rd.path[0]:
                rd.path = rd.path[1:]
                data = HttpMsgData(dest= entry.remote, type= '/'.join(rd.path), 
                                   data= rd.model_dump())
                resp = await self.core.web_l.api_send(data)
                if resp is not None:
                    return (True, web.json_response(resp))
                return (True, web.json_response(SendOk(ok=False).model_dump()))
        #prüfen ob einträge für allgemeine auth handler ist
        auth_resp = await self._auth.handler(request, rd)
        if auth_resp[0]:
            return auth_resp
        #call für dieses Modul
        match "/".join(rd.path):
            case 'get_allowed_moduls':
                #self.core.log.critical(rd)
                if rd.open_id and (self.core.const.app in rd.open_id['app'] or rd.open_id['app'] == '*'):
                    try:
                        data = Moduls()
                        data.append({'mod': 'app', 'src': '/js/mod/app'})
                        self.core.log.debug("/".join(rd.path))
                        #self.core.log.debug(rd)
                        return (True, web.json_response(data.model_dump()))
                    except Exception as e:
                        self.core.log.error(e)
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'app/load_list':
                if rd.open_id:
                    data = Apps()
                    for app, info in self._apps.items():
                        if (app in rd.open_id['app'] or rd.open_id['app'] == '*') and info.time > time.time()-3600:
                            data.append(info)
                    data.sort()
                    return (True, web.json_response(data.model_dump()))
                return (True, web.json_response(SendOk(ok=False).model_dump()))
            case _:
                self.core.log.debug("/".join(rd.path))
                self.core.log.debug(rd)
        return
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        try:
            await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        except Exception as e:
            self.core.log.error(e)

    async def _astart(self):
        self.core.log.debug('starte api')
