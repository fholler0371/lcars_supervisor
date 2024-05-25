from aiohttp import web
import aiohttp
import urllib.parse as up
import json

from corelib import Core
from corelib.aio_property import aproperty
from httplib.models import HttpRequestData, SendOk

from aioauth.models import GetClientId, ClientIdSecret, Code, Token
from httplib.models import HttpMsgData, RedirectUrl, HttpRequestData

class Client:
    def __init__(self, core: Core):
        self.core: Core = core
        self.callback = ''
        self._clientid = None
        self._secret = None
        
    @aproperty
    async def clientid(self):
        if self._clientid is None:
            pass
            data = GetClientId(callback=self.callback, app=self.core.const.app)
            resp = await self.core.web_l.msg_send(HttpMsgData(dest='web_auth', type='get_client_data', data=data))
            if resp is not None:
                resp = ClientIdSecret.model_validate(resp)
                self._clientid = resp.clientid
                self._secret = resp.secret
        return self._clientid
        
    async def handler(self, request: web.Request, rd:HttpRequestData) -> None:
        match "/".join(rd.path):
            case "get_login_link":
                try:
                    try: # ein level runter
                        rd = HttpMsgData.model_validate(rd.data)
                    except Exception as e:
                        self.core.log.error(e) 
                    try: # ein level runter
                        rd = HttpRequestData.model_validate(rd.data)
                    except Exception as e:
                        self.core.log.error(e) 
                    url = rd.scheme
                    self.callback = url = f"{url}://{rd.host}/"
                    self.callback += 'callback.html' if self.core.const.app == 'web_base' else f'{self.core.const.app.split('_')[-1]}/callback.html'
                    url += f'auth/login.html?response_type=code&redirect_uri={up.quote(self.callback)}'
                    client_id = await self.clientid
                    if client_id is None:
                        return (True, web.json_response(SendOk(ok=False).model_dump()))
                    url += f'&client_id={await self.clientid}&scope=openid+profile+name+role+app&state='
                    return (True, web.json_response(RedirectUrl(url=url).model_dump()))
                except Exception as e:
                    self.core.log.error(e) 
            case "validate_code":
                try:
                    url = rd.scheme
                    self.callback = url = f"{url}://{rd.host}/"
                    self.callback += 'callback.html' if self.core.const.app == 'web_base' else f'{self.core.const.app.split('_')[-1]}/callback.html'
                    try:
                        rd = HttpMsgData.model_validate(rd.data)
                        rd = HttpRequestData.model_validate(rd.data)
                    except:
                        pass
                    data = Code.model_validate_json(rd.data)
                    post_data = (('grant_type', 'code'),
                                 ('client_id', await self.clientid),
                                 ('client_secret', self._secret),
                                 ('redirect_uri', self.callback),
                                 ('code', data.code))
                    try:
                        resp = await self.core.web_l.post_raw_url(f"{url}api/auth/token", post_data)
                        self.core.log.critical(resp) 
                        if resp is None:
                            return (True, web.json_response(SendOk(ok=False).model_dump()))
                        else:
                            self.core.log.critical(resp) 
                            return (True, web.json_response(json.loads(resp)))
                    except Exception as e:
                        self.core.log.error(e)                 
                except Exception as e:
                    self.core.log.error(e)                 
            case "refresh_token":
                try:
                    url = rd.scheme
                    url = f"{url}://{rd.host}/"                    
                    try:
                        rd = HttpMsgData.model_validate(rd.data)
                        rd = HttpRequestData.model_validate(rd.data)
                    except:
                        pass
                    data = Token.model_validate_json(rd.data)
                    post_data = (('grant_type', 'refresh_token'),
                                 ('client_id', await self.clientid),
                                 ('client_secret', self._secret),
                                 ('code', data.token))
                    self.core.log.critical(post_data)
                    try:
                        resp = await self.core.web_l.post_raw_url(f"{url}api/auth/token", post_data)
                        self.core.log.critical(resp) 
                        if resp is None:
                            return (True, web.json_response(SendOk(ok=False).model_dump()))
                        else:
                            return (True, web.json_response(json.loads(resp)))
                    except Exception as e:
                        self.core.log.error(e)                 
                except Exception as e:
                    self.core.log.error(e)                 
        return (False, None)
