import tomllib
import time
import aiohttp
import pathlib

from corelib import BaseObj, Core
import aioyamllib
from httplib.models import HttpMsgData
from models.notify import NotifyApp, NotifyMessage

from . import models

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
            secret = self.core.secret.withings
            response = await session.post(url="https://wbsapi.withings.net/v2/oauth2",
                                          data={"action": "requesttoken",
                                                'grant_type': "refresh_token",
                                                'client_id': secret['client'],
                                                'client_secret': secret['secret'],
                                                'refresh_token': self._data['refresh_token']},
                                          headers={"Content-Type": "application/json"})
            data = await response.json()
            if data['status'] == 0:
                data = data['body']
                await self.set_token(data['access_token'], data['refresh_token'], int(time.time() + data['expires_in'] - 900))
            else:
                self._data = None
            return self._data['token']


class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._device = {}
        self._notify_token = None
                
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        self.token = _token()
                   
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.get_device_data)
        await self.core.call_random(20, self.register_notify)

    async def _astop(self):
        self.core.log.debug('stoppe api')
        
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

    async def get_device_data(self):
        await self.core.call_random(3 * 3600, self.get_device_data)
        try:
            token = await self.token.get()
            if token is None and self._notify_token is not None:
                data = NotifyMessage(token=self._notify_token, text='Die App muss neu angemeldet werden')
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
                        self.core.log.debug(f'{rec.model} - Batterie: {rec.battery}')
                        if rec.battery == 'low' and self._notify_token is not None:
                            data = NotifyMessage(token=self._notify_token, text=f'Die Battery von \"{rec.model}\" ist fast leer')
                            await self.core.web_l.msg_send(HttpMsgData(dest='web_notify', type='notify_message', data=data))

        except Exception as e:
            self.core.log.error(e)
