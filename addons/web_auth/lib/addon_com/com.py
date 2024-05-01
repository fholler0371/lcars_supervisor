from aiohttp import web
import pydantic
import json

import aiotomllib
import cryptlib
import aiodatabase

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk
from aioauth.models import GetClientId, ClientIdSecret

import addon_com.db as db_settings

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        self._aes = None
        self.core.log.debug(f"sqlite://{self.core.path.data}/apps.sqlite3")
        self._apps_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/apps.sqlite3")
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
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
        
    async def _astart(self):
        self.core.log.debug('starte com')
