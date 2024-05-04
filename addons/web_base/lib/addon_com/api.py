from aiohttp import web
import pydantic
import json

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, HttpMsgData
import aioauth

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._auth = aioauth.Client(self.core)
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        #Umleiten von api calls
        self.core.log.debug("/".join(rd.path))
        for entry in self.core.web._handlers:
            if entry.remote and entry.domain == rd.path[0]:
                rd.path = rd.path[1:]
                data = HttpMsgData(dest= entry.remote, type= '/'.join(rd.path), 
                                   data= rd.model_dump())
                resp = await self.core.web_l.api_send(data)
                if resp is not None:
                    return (True, web.json_response(resp))
        #prüfen ob einträge für allgemeine auth handler ist
        auth_resp = await self._auth.handler(request, rd)
        if auth_resp[0]:
            return auth_resp
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
