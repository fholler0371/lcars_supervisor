from aiohttp import web
import aiohttp
import json
import tomllib
import urllib.parse
import time

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.auth import Moduls
from models.network import IpData
import aioauth

import aiotomllib


class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._state = ''
        self._auth = aioauth.Client(self.core)
                
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        #prüfen ob einträge für allgemeine auth handler ist
        self.core.log.critical('v2')
        self.core.log.critical(rd)
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
                if rd.open_id and ('withings_sec' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = Moduls()
                    data.append({'mod': 'withings_setup', 'src': '/withings/js/mod/withings_setup'})
                    return (True, web.json_response(data.model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'setup/get_url':
                self.core.log.debug('Ask for url')
                bc = rd.data.data
                url = ''
                if bc['open_id'] and ('withings_sec' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    with open("/lcars/config/secret.toml", "rb") as f:
                        config = tomllib.load(f).get('withings', {})
                        url = "https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id="
                        url += f"{config['client']}&scope=user.info,user.metrics,user.activity&redirect_uri="
                        url += urllib.parse.quote_plus(config['callback'])
                        self._state = str(int(time.time()))
                        url += f"&state={self._state}"
                    return (True, web.json_response(SendOk(data={'url': url}).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'user/fritzlink':
                self.core.log.debug('get fritzlinky')
                bc = rd.data.data
                if bc['open_id'] and ('withings' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    return (True, web.json_response({"ok" :True, "link": self._fritzlink}))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case _:
                self.core.log.critical('/'.join(rd.path))
                
    async def receive_code(self, code, state):
        if self._state == state:
            async with aiohttp.ClientSession() as session:
                with open("/lcars/config/secret.toml", "rb") as f:
                    config = tomllib.load(f).get('withings', {})
                response = await session.post(url="https://wbsapi.withings.net/v2/oauth2",
                                              data={"action": "requesttoken",
                                              	    "grant_type": "authorization_code",
	                                                "client_id": config['client'],
                                                    "client_secret": config['secret'],
	                                                "code": code,
	                                                "redirect_uri": config['callback']},
                                              headers={"Content-Type": "application/json"})
                data = await response.json()
                data = data['body']
                await self.core.web_l.msg_send(HttpMsgData(dest='withings', 
                                                           type='set_token', 
                                                           data={'refresh_token': data['refresh_token'],
                                                                 'token': data['access_token'],
                                                                 'timeout': int(time.time() + data['expires_in'] - 900)}))
                
    async def add_scopes(self):
        self.core.log.debug('scopes aktualiesieren')
        await self.core.call_random(12*3600 , self.add_scopes) #
        await self.core.web_l.msg_send(HttpMsgData(dest='web_auth', type='set_scopes', data=['withings', 'withings_sec']))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.add_scopes)
