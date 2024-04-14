import aioretry
import aiohttp

from corelib import BaseObj, Core

from .local_keys import LocalKeys


MAX_RETRY = 7
def retry_policy(info: aioretry.RetryInfo) -> aioretry.RetryPolicyStrategy:
    return info.fails > MAX_RETRY, (2 ** info.fails) * 0.1


class ClientLocal(BaseObj):
    def __init__(self, core: Core, sv: bool= False) -> None:
        BaseObj.__init__(self, core)
        
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
        
    async def get(self, url: str, dest: str = 'local', version: int = 1) -> any:
        try:
            return await self._get(f'cli/{version}/{url}', dest)
        except Exception as e:
            self.core.log.error(e)
        return None

    @aioretry.retry(retry_policy)        
    async def _post(self, url: str, data: dict, dest: str) -> None:
        try:
            if dest == 'local':
                host = '127.0.0.1:1234'
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

    async def post(self, url: str, data: dict= {}, dest: str = 'local', version: int = 1) -> any:
        try:
            return await self._post(f'cli/{version}/{url}', data, dest)
        except Exception as e:
            self.core.log.error(e)
        return None
