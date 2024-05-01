from aiohttp import web
import mimetypes
import aiofiles
import pydantic
import json

import aiotomllib
import cryptlib
import aiodatabase

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from aioauth.models import GetClientId, ClientIdSecret
from aioauth.models import UserData

import addon_com.db as db_settings


TEXT_FILES = ['text/html', 'text/javascript'] 

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        self._aes = None
        self._apps_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/apps.sqlite3")
             
    async def static(self, path: str) -> tuple:
        if path == '':
            path = 'index.html'
        file_name = self.core.path.web / path
        if file_name.exists():
            mime = mimetypes.guess_type(file_name)[0]
            if mime in TEXT_FILES:
                async with aiofiles.open(file_name) as f:
                    return (True, web.Response(text=await f.read(), content_type=mime, headers={'X-Raw': '1'})) 
        else:
            return (True, web.Response(status=418))
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'messages/relay':
                msg = HttpMsgData.model_validate(rd.data)
                relay_rd = HttpRequestData.model_validate(msg.data)
                return await self.static('/'.join(relay_rd.path))
            case 'messages/get_client_data':
                msg = rd.data
                data = GetClientId.model_validate(msg.data)
                try:
                    row = await self._apps_db.table('app').exec('get_app', {'name': data.app})
                    if row is None: # erstellen einer neuen app
                        await self._apps_db.table('app').exec('insert', {'name': data.app, 'type': 'outh2'})
                        row = await self._apps_db.table('app').exec('get_app', {'name': data.app})
                    app_id = row['id']
                    row = await self._apps_db.table('oauth').exec('get_client_data', {'app_id': app_id})
                    if row is None: # erstellen einer neuen clientid, secret
                        await self._apps_db.table('oauth').exec('insert', 
                                                                {'app_id': app_id, 
                                                                 'clientid': cryptlib.key_gen(32),
                                                                 'secret': self._aes.encrypt(cryptlib.key_gen(64)),
                                                                 'callback': data.callback})
                        row = await self._apps_db.table('oauth').exec('get_client_data', {'app_id': app_id})
                    return (True, web.json_response(ClientIdSecret(clientid=row['clientid'], secret=self._aes.decrypt(row['secret'])).model_dump()))
                except Exception as e:
                    self.core.log.error(e)
                #await self.core.web.add_handler(data)
                return (True, web.json_response(SendOk().model_dump()))  
            case 'messages/user_add':
                msg = HttpMsgData.model_validate(rd.data)
                data = UserData.model_validate_json(msg.data)
                self.core.log.debug(data) #>>>>>>>>>>>>>>>>
                return (True, web.json_response(SendOk().model_dump()))
            case _:   
                msg = HttpMsgData.model_validate(rd.data)
                self.core.log.debug(rd)
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
        try:
            db = self._apps_db
            db.add_table(db_settings.App())
            db.add_table(db_settings.Oauth())
            await db.setup()
        except Exception as e:
            self.core.log.error(e)
        
    async def register_web_app(self)->None:
        self.core.log.debug('do register')
        await self.core.call_random(300, self.register_web_app)
        data = HttpHandler(domain='auth', acl=None, 
                           remote=f'{await self.core.web_l.hostname}.{self.core.const.app}')
        try:
            await self.core.web_l.msg_send(HttpMsgData(dest='web_base', type='register_web_app', data=data))
        except Exception as e:
            self.core.log.error(e)
 
    async def _astart(self):
        self.core.log.debug('starte com')
        await self.core.call_random(10, self.register_web_app)
