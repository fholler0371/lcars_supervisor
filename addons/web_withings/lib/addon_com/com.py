from aiohttp import web
import mimetypes
import aiofiles

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, HttpMsgData
from models.auth import App

TEXT_FILES = ['text/html', 'text/javascript'] 


class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def static(self, path: str) -> tuple:
        if path == '':
            path = 'index.html'
        file_name = self.core.path.web / path
        if file_name.exists():
            mime = mimetypes.guess_type(file_name)[0]
            if mime in TEXT_FILES:
                async with aiofiles.open(file_name) as f:
                    return (True, web.Response(text=await f.read(), content_type=mime, headers={'X-Raw': '1'})) 
        elif path == 'pem':
            file_name = self.core.path.data / 'rsa_public.pem'
            if file_name.exists():
                async with aiofiles.open(str(file_name)) as f:
                    return (True, web.Response(text=await f.read(), headers={'X-Raw': '1'})) 
        else:
            self.core.log.critical(file_name)
            return (True, web.Response(status=418))
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'messages/relay':
                msg = HttpMsgData.model_validate(rd.data)
                relay_rd = HttpRequestData.model_validate(msg.data)
                if relay_rd.path == ['auth']:
                    await self.core.call(self.core.api.receive_code, relay_rd.data.get('code'), relay_rd.data.get('state'))
                    relay_rd.path = ['auth.html']
                return await self.static('/'.join(relay_rd.path))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='docker'))

    async def register_web_app(self)->None:
        self.core.log.debug('do register')
        await self.core.call_random(300, self.register_web_app)
        data = HttpHandler(domain='withings', acl=None, 
                           remote=f'{await self.core.web_l.hostname}.{self.core.const.app}')
        try:
            await self.core.web_l.msg_send(HttpMsgData(dest='web_base', type='register_web_app', data=data))
        except Exception as e:
            self.core.log.error(e)
        data = App(app='withings',
                   url='/withings',
                   icon='/css/images/human-handsdown.svg',
                   label='Withings')
        try:
            await self.core.web_l.msg_send(HttpMsgData(dest='web_base', type='register_app', data=data))
        except Exception as e:
            self.core.log.error(e)

    async def _astart(self):
        self.core.log.debug('starte com')
        await self.core.call_random(10, self.register_web_app)
