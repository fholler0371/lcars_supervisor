from aiohttp import web
import mimetypes
import string
import random
import aiofiles
import json

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, HttpMsgData, SendOk
from models.auth import App
from models.notify import NotifyApp, NotifyMessage
from models.basic import StringEntry
from models.msg import MSG_DIRECT

import aiodatabase

import addon_com.db as db_settings

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
        msg_type = 0
        try:
            rd.data = json.loads(rd.data)
            msg_type = rd.data.get('type', 0)
        except:
            ...
        if msg_type == MSG_DIRECT and rd.auth:
            match '/'.join(rd.path):
                case 'register_notify_app':
                    data = NotifyApp.model_validate(rd.data)
                    resp = await self._apps_db.table('apps').exec('get_token_by_app', {'app': data.app})
                    if not resp:
                        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
                        await self._apps_db.table('apps').exec('add', {'app': data.app, 'icon': data.icon, 'label': data.label, 'token': token})
                    else:
                        token = resp['token']
                    token = StringEntry(data= token)
                    return (True, web.json_response(SendOk(data=token.data).model_dump()))
                case 'notify_message':
                    data = rd.data
                    resp = await self._apps_db.table('apps').exec('get_id_by_token', {'token': data['token']})
                    if not resp:
                        return (True, web.json_response({'ok': True}))
                    app_id = resp['id']
                    self.core.log.critical(data)
                    resp = await self._msg_db.table('message').exec('get_timestamp_by_md5', {'md5': data['md5']})    
                    if resp is not None:
                        return (True, web.json_response({'ok': True}))
                    await self._msg_db.table('message').exec('add', {'app': app_id, 'type': data['level'], 'text': data['text'], 
                                                                     'md5': data['md5'], 'timestamp': data['timestamp']})
                    return (True, web.json_response({'ok': True}))
                case _:
                    self.core.log.critical(rd)
        else:       
            match '/'.join(rd.path):
                case 'messages/relay':
                    msg = HttpMsgData.model_validate(rd.data)
                    relay_rd = HttpRequestData.model_validate(msg.data)
                    return await self.static('/'.join(relay_rd.path))
                case 'messages/register_notify_app':
                    if rd.auth:
                        data = NotifyApp.model_validate(rd.data.data)
                        resp = await self._apps_db.table('apps').exec('get_token_by_app', {'app': data.app})
                        if not resp:
                            token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
                            await self._apps_db.table('apps').exec('add', {'app': data.app, 'icon': data.icon, 'label': data.label, 'token': token})
                        else:
                            token = resp['token']
                        token = StringEntry(data= token)
                        return (True, web.json_response(SendOk(data=token.model_dump()).model_dump()))
                case 'messages/notify_message':
                    if rd.auth:
                        data = NotifyMessage.model_validate(rd.data.data)
                        resp = await self._apps_db.table('apps').exec('get_id_by_token', {'token': data.token})
                        if not resp:
                            return (False, web.json_response({}))
                        app_id = resp['id']
                        resp = await self._msg_db.table('message').exec('get_timestamp_by_md5', {'md5': data.md5})    
                        self.core.log.error(resp)                    
                        if resp is not None:
                            return (True, web.json_response({}))
                        await self._msg_db.table('message').exec('add', {'app': app_id, 'type': data.type, 'text': data.text, 'md5': data.md5, 'timestamp': data.timestamp})
                        return (True, web.json_response({}))
                case _:
                    self.core.log.error(rd)
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='docker'))

    async def register_web_app(self)->None:
        self.core.log.debug('do register')
        await self.core.call_random(300, self.register_web_app)
        data = HttpHandler(domain='notify', acl=None, 
                           remote=f'{await self.core.web_l.hostname}.{self.core.const.app}')
        try:
            await self.core.web_l.msg_send(HttpMsgData(dest='web_base', type='register_web_app', data=data))
        except Exception as e:
            self.core.log.error(e)
        data = App(app='notify',
                   url='/notify',
                   icon='/img/mdi/information-variant.svg',
                   label='Notify')
        try:
            await self.core.web_l.msg_send(HttpMsgData(dest='web_base', type='register_app', data=data))
        except Exception as e:
            self.core.log.error(e)

    async def _astart(self):
        self.core.log.debug('starte com')
        await self.core.call_random(10, self.register_web_app)
        try:
            self._apps_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/apps.sqlite3")
            self._apps_db.add_table(db_settings.Apps())
            await self._apps_db.setup()
            self._msg_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/messages.sqlite3")
            self._msg_db.add_table(db_settings.Message())
            await self._msg_db.setup()

            # self._budget_db.add_table(db_settings.Budgets())
            # self._budget_db.add_table(db_settings.Bought())
            # self._food_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/food.sqlite3")
            # self._food_db.add_table(db_settings.FoodBought())
        except Exception as e:
            self.core.log.error(repr(e))
