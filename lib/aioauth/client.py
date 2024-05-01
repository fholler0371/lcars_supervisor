from aiohttp import web
import urllib.parse as up

from corelib import Core
from corelib.aio_property import aproperty
from httplib.models import HttpRequestData, SendOk

from aioauth.models import GetClientId, ClientIdSecret
from httplib.models import HttpMsgData, RedirectUrl

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
                    url = x if (x := request.headers.get('X-Forwarded-Scheme')) else request.scheme
                    self.callback = url = f"{url}://{request.host}/"
                    self.callback += 'callback.html' if self.core.const.app == 'web_base' else f'{self.core.const.app}/callback.html'
                    url += f'auth/login.html?response_type=code&redirect_uri={up.quote(self.callback)}'
                    url += f'&client_id={await self.clientid}&scope=openid+profile+role&state='
                    return (True, web.json_response(RedirectUrl(url=url).model_dump()))
                except Exception as e:
                    self.core.log.debug(e) 
        return (False, None)
