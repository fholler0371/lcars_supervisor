from pathlib import Path
import aiohttp
import tomllib
import time

from corelib import BaseObj, Core
import aiotomllib
from models.notify import NotifyApp, NotifyMessage
from httplib.models import HttpMsgData, HttpHandler, HttpRequestData


class ApiXML(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
                   
    async def _ainit(self):
        self.core.log.debug('init api-xml')
        cfg = (await aiotomllib.loader(Path('/lcars/config/secret.toml'))).get('homematic', {})
        self._ip = cfg.get('ip')
        self._token = cfg.get('token')
        self._notify_token = None

    async def _astart(self):
        self.core.log.debug('starte api-xml')
        await self.core.call_random(30, self._check_notifications)
        await self.core.call_random(20, self._register_notify)

    async def _astop(self):
        self.core.log.debug('stoppe api-xml')
        
    async def _check_notifications(self):
        await self.core.call_random(3600, self._check_notifications)
        try:
            url = f"http://{self._ip}/addons/xmlapi/systemNotificationClear.cgi?sid={self._token}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.core.log.error('Konnte Notifications nicht löschen')
                        return
        except Exception as e:
            self.core.log.error(repr(e))
        try:
            url = f"http://{self._ip}/addons/xmlapi/systemNotification.cgi?sid={self._token}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.core.log.error('Konnte Notifications nicht laden')
                        return
                    entries = (await response.text()).split('<notification')[1:]
                    for entry in entries:
                        item = entry.split("name='")[1].split("'")[0]
                        _, device, type = item.split('.')
                        device = device.split(':')[0]
                        self.core.log.debug(f"{device} {type}")
        except Exception as e:
            self.core.log.error(repr(e))

    async def _register_notify(self)->None:
        self.core.log.debug('get_notify_token')
        if self._notify_token is None:
            await self.core.call_random(60, self._register_notify)
            data = NotifyApp(label= self.core.cfg.manifest['label_short'],
                             icon= self.core.cfg.manifest['icon'],
                             app= self.core.cfg.manifest['name'])
            self.core.log.critical(data)
            resp = await self.core.web_l.msg_send(HttpMsgData(dest='web_notify', type='register_notify_app', data=data))
            if resp and resp['ok']:
                self._notify_token = resp['data']['data']
            self.core.log.debug(f"NotifyToken: {self._notify_token}")
