from aiohttp import web
import urllib.parse as up

from corelib import Core
from corelib.aio_property import aproperty
from httplib.models import HttpRequestData, SendOk

from aioauth.models import GetClientId
from httplib.models import HttpMsgData

class Client:
    def __init__(self, core: Core):
        self.core: Core = core
        self.callback = ''
        self._client = None
        
    @aproperty
    async def clientid(self):
        if self._client is None:
            pass
            data = GetClientId(callback=self.callback, app=self.core.const.app)
            self.core.log.debug(await self.core.web_l.msg_send(HttpMsgData(dest='web_auth', type='get_client_data', data=data)))
            self.core.log.debug(data)
        return self._client
        
    async def handler(self, request: web.Request, rd:HttpRequestData) -> None:
        match "/".join(rd.path):
            case "get_login_link":
                url = x if (x := request.headers.get('X-Forwarded-Scheme')) else request.scheme
                self.callback = url = f"{url}://{request.host}/"
                self.callback += 'callback.html' if self.core.const.app == 'web_base' else f'{self.core.const.app}/callback.html'
                url += f'auth/login.html?response_type=code&redirect_uri={up.quote(self.callback)}'
                self.core.log.debug(url)
                self.core.log.debug(self.callback)
                self.core.log.debug(request.host)
                self.core.log.debug(await self.clientid)
                
                # &client_id=29352735982374239857
                # &scope=create+delete
                # &state=xcoivjuywkdkhvusuye3kch
                return (True, web.json_response(SendOk().model_dump()))
        self.core.log.debug(rd)
        return (False, None)
