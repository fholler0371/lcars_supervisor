import asyncio
import aioretry
import aiohttp
import time

from corelib import BaseObj, Core
from corelib.aio_property import aproperty
from models.basic import StringList
from models.network import Hostname

from .local_keys import LocalKeys
from .models import HttpMsgData


MAX_RETRY = 7
def retry_policy(info: aioretry.RetryInfo) -> aioretry.RetryPolicyStrategy:
    return info.fails > MAX_RETRY, (2 ** info.fails) * 0.1


class ClientLocal(BaseObj):
    def __init__(self, core: Core, sv: bool= False) -> None:
        BaseObj.__init__(self, core)
        self._hostname = None
        self._parent_ip = None
        self._app_list_valid = 0
        self._app_list = []
        
    async def _ainit(self):
        self.local_keys = LocalKeys(self.core)
        await self.local_keys._ainit(sv=True)
        self.session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=1,sock_read=5)

    @aioretry.retry(retry_policy)        
    async def _get(self, url: str, dest: str) -> None:
        try:
            if dest == 'local':
                host = '127.0.0.1:1234'
                key = self.local_keys.local
            elif dest == 'gateway':
                host = 'gateway:1235'
                key = self.local_keys.local
            elif dest == 'parent':
                if self._parent_ip is None:
                    cmd = "ip route | grep default | awk '{ print $3 }'"
                    p = await asyncio.subprocess.create_subprocess_shell(
                                  cmd, 
                                  stderr=asyncio.subprocess.PIPE, 
                                  stdout=asyncio.subprocess.PIPE)
                    stdout, _ = await p.communicate()
                    self._parent_ip = stdout.decode().split('\n')[0]
                host = f'{self._parent_ip}:1234'
                key = self.local_keys.local
            else:
                host = f'{dest}:1235'
                key = self.local_keys.local
            async with aiohttp.ClientSession(headers={'X-Auth':key}, timeout=self.session_timeout) as session:
                async with session.get(f'http://{host}/{url}') as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.core.log.error(f'Abfrage von {url} gibt Kode {response.status} zurück')
                    if str(response.status).startswith('4'):
                        return None
        except Exception as e:
            self.core.log.error(e)
            raise(e)
        return None
        
    async def get(self, url: str, dest: str = 'local', version: int = 1, endpoint: str = 'cli') -> any:
        try:
            return await self._get(f'{endpoint}/{version}/{url}', dest)
        except Exception as e:
            self.core.log.error(e)
        return None

    @aioretry.retry(retry_policy)        
    async def _post(self, url: str, data: dict, dest: str) -> None:
        try:
            if dest == 'local':
                host = '127.0.0.1:1234'
                key = self.local_keys.local
            elif dest == 'gateway':
                host = 'gateway:1235'
                key = self.local_keys.local
            elif dest == 'parent':
                if self._parent_ip is None:
                    cmd = "ip route | grep default | awk '{ print $3 }'"
                    p = await asyncio.subprocess.create_subprocess_shell(
                                  cmd, 
                                  stderr=asyncio.subprocess.PIPE, 
                                  stdout=asyncio.subprocess.PIPE)
                    stdout, _ = await p.communicate()
                    self._parent_ip = stdout.decode().split('\n')[0]
                host = f'{self._parent_ip}:1234'
                key = self.local_keys.local
            else:
                host = f'{dest}:1235'
                key = self.local_keys.local
            async with aiohttp.ClientSession(headers={'X-Auth':key}, timeout=self.session_timeout) as session:
                async with session.post(f'http://{host}/{url}', json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.core.log.error(f'Abfrage von {url} gibt Kode {response.status} zurück')
                    if str(response.status).startswith('4'):
                        return None
        except Exception as e:
            self.core.log.error(e)
            raise(e)
        return None

    async def post(self, url: str, data: dict= {}, dest: str = 'local', version: int = 1, endpoint: str = 'cli') -> any:
        try:
            return await self._post(f'{endpoint}/{version}/{url}', data, dest)
        except Exception as e:
            self.core.log.error(e)
        return None

    @aproperty
    async def hostname(self):
        if self._hostname is None:
            resp = await self.get('network/hostname', dest='gateway', endpoint='com')
            data = Hostname.model_validate(resp)
            self._hostname = data.hostname
        return self._hostname

    @aproperty
    async def app_list(self):
        if self._app_list_valid < time.time():
            resp = await self.get('network/app_list', dest='gateway', endpoint='com')
            if resp is not None:
                data = StringList.model_validate(resp)
                self._app_list = data.data
                self._app_list_valid = time.time() + self.core.random(600)
        return self._app_list
    
    async def msg_send(self, data: HttpMsgData):
        dest_app = None
        if '.' in data.dest:
            dest_app = data.dest
        else:
            for app in await self.app_list:
                if app.endswith(f'.{data.dest}'):
                    dest_app = app
        if dest_app is None:
            return
        hostname = dest_app.split('.')[0]
        if hostname == await self.core.web_l.hostname:
            app = dest_app.split('.')[1]
            resp = await self.post(f'messages/{data.type}', data=data.model_dump(), dest=app, endpoint='com')
            self.core.log.debug(resp)
