from aiohttp import web
import aiohttp
import pathlib
import aioyamllib
import time
import tomllib

from corelib import BaseObj, Core
from httplib.models import HttpMsgData, HttpHandler, HttpRequestData, SendOk
from . import models

from models.notify import NotifyApp, NotifyMessage

import aiodatabase

import addon.db as db_settings


class _token:
    def __init__(self) -> None:
        self.file = pathlib.Path('/lcars/data/token.yml')
        self._data = None
        if self.file.exists():
            self._data = aioyamllib._safe_load(self.file)
            
    async def set_token(self, token, refresh_token, timeout):
        self._data = {'token': token,
                      'refresh_token': refresh_token, 
                      'timeout': timeout}
        await self.save()
    
    async def save(self):
        await aioyamllib.dump(self.file, self._data)
        
    async def get(self):
        if self._data['timeout'] > time.time():
            return self._data['token']
        else:
            async with aiohttp.ClientSession() as session:
                with open("/lcars/config/secret.toml", "rb") as f:
                    config = tomllib.load(f).get('withings', {})
                response = await session.post(url="https://wbsapi.withings.net/v2/oauth2",
                                              data={"action": "requesttoken",
                                                    'grant_type': "refresh_token",
                                                    'client_id': config['client'],
                                                    'client_secret': config['secret'],
                                                    'refresh_token': self._data['refresh_token']},
                                              headers={"Content-Type": "application/json"})
                data = await response.json()
                if data['status'] == 0:
                    data = data['body']
                    await self.set_token(data['access_token'], data['refresh_token'], int(time.time() + data['expires_in'] - 900))
                else:
                    self._data = None
            return self._data['token']

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self.token = _token()
        self._notify_token = None
        self._device = {}
        #self._state_name = pathlib.Path('/lcars/data/ip_state.yml')
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        if rd.path[0] == 'messages':
#            msg = HttpMsgData.model_validate(rd.data)
            match rd.path[1]:
            #     case 'get_ip':
            #         data = IpData(ip4=self._state.ip4)
            #         return (True, web.json_response(data.model_dump()))
            #     case 'get_all_ip':
            #         #self.core.log.critical(self._state)
            #         data = IpData(ip4=self._state.ip4, prefix=self._state.prefix, ip6=self._state.ip6, home_ip6=self._state.home_ip6)
            #         #self.core.log.critical(data)
            #         return (True, web.json_response(data.model_dump()))
                case 'messages/set_token':
                    data = rd.data.data
                    await self.token.set_token(data['token'], data['refresh_token'], data['timeout'])
                    return (True, web.json_response({}))
                case 'sm':
                    data = rd.data.data
                    match rd.path[2]:
                        case 'get_sensor':
                            table, sensor = data['sensor'].split('.')
                            if table == 'body':
                                res = await self._data_db.table('vital').exec('get_last_by_type', {'type': sensor})
                                if res:
                                    return (True, web.json_response(SendOk(data={'value': res['value']}).model_dump()))
                                else:
                                    return (True, web.json_response(SendOk(ok=False).models_dump()))
                        case 'get_history':
                            _table, _sensor = data['sensor'].split('.')
                            _interval = 30 * 86400
                            if _table == 'body':
                                res = await self._data_db.table('vital').exec('get_history', {'type': _sensor, 'date': int(time.time() - _interval)})
                                if res:
                                    return (True, web.json_response(SendOk(data=res).model_dump()))
                                else:
                                    return (True, web.json_response(SendOk(ok=False).models_dump()))
                            self.core.log.critical(rd)
                            self.core.log.critical('xXx 2')
                            self.core.log.critical(data)
                case _:
                     self.core.log.critical(rd)
                        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='lcars_docker'))
        self._data_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/data.sqlite3")
        self._data_db.add_table(db_settings.Vital())
        
    async def get_device_data(self):
        await self.core.call_random(3 * 3600, self.get_device_data)
        try:
            token = await self.token.get()
            if token is None and self._notify_token is not None:
                data = NotifyMessage(token=self._notify_token, text=f'Die App muss neu angemeldet werden')
                await self.core.web_l.msg_send(HttpMsgData(dest='web_notify', type='notify_message', data=data))
                return
            async with aiohttp.ClientSession() as session:
                response = await session.post(url="https://wbsapi.withings.net/v2/user",
                                              data={"action": "getdevice"},
                                              headers={"Content-Type": "application/json",
                                                       'Authorization': f"Bearer {token}"})
                self.core.log.error(response)
                data = await response.json()
                if data['status'] == 0:
                    for device in data['body']['devices']:
                        rec = models.Device.model_validate(device)
                        self._device[rec.id] = rec
                        if rec.battery == 'low' and self._notify_token is not None:
                            data = NotifyMessage(token=self._notify_token, text=f'Die Battery von \"{rec.model}\" ist fast leer')
                            await self.core.web_l.msg_send(HttpMsgData(dest='web_notify', type='notify_message', data=data))

        except Exception as e:
            self.core.log.error(e)

    async def register_notify(self)->None:
        self.core.log.debug('get_notify_token')
        if self._notify_token is None:
            await self.core.call_random(60, self.register_notify)
            data = NotifyApp(label='Withings',
                            icon='/css/images/human-handsdown.svg',
                            app='withings')
            resp = await self.core.web_l.msg_send(HttpMsgData(dest='web_notify', type='register_notify_app', data=data))
            if resp and resp['ok']:
                self._notify_token = resp['data']['data']
            self.core.log.debug(f"NotifyToken: {self._notify_token}")
           
    async def _astart(self):
        self.core.log.debug('starte com')
        await self.core.call_random(30, self.get_device_data)
        await self.core.call_random(20, self.register_notify)
        await self._data_db.setup()

    async def _astop(self):
        self.core.log.debug('stoppe com')
