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
    def __init__(self, core) -> None:
        self.file = pathlib.Path('/lcars/data/token.yml')
        self.__core = core
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
            secret = self.__core.secret.withings
            async with aiohttp.ClientSession() as session:
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
                
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        self.token = _token(self.core)
                   
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.get_device_data)

    async def _astop(self):
        self.core.log.debug('stoppe api')
        
    async def get_device_data(self):
        await self.core.call_random(3 * 3600, self.get_device_data)
        try:
            token = await self.token.get()
            if token is None and self._notify_token is not None:
                await self.core.notify.send('Die App muss neu angemeldet werden')
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
                        if rec.battery == 'low':
                            await self.core.notify.send(f'Die Battery von \"{rec.model}\" ist fast leer')

        except Exception as e:
            self.core.log.error(e)
