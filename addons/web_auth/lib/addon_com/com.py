from aiohttp import web
import pydantic
import json

import aiotomllib
import cryptlib

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk
from aioauth.models import GetClientId


class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        self._aes = None
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'messages/get_client_data':
                msg = rd.data
                data = GetClientId.model_validate(msg.data)
                try:
                    self.core.log.debug(data)
                    self.core.log.debug(x := self._aes.encode(data.callback))
                    self.core.log.debug(self._aes.decode(x))
                except Exception as e:
                    self.core.log.error(e)
                #await self.core.web.add_handler(data)
                return (True, web.json_response(SendOk().model_dump()))
            
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='docker'))
        try:
            toml = await aiotomllib.loader(self.core.path.config / 'secret.toml')
            _aes_key = toml.get('aes_app_key', 'ChangeMe')
            if _aes_key == 'ChangeMe':
                self.core.log.critical('Brauche gültigen AES-KEY in secret.toml')
                self.core.running.set()
                return
            self._aes = cryptlib.Aes(_aes_key)
        except Exception as e:
            self.core.log.error(e)

    async def _astart(self):
        self.core.log.debug('starte com')
