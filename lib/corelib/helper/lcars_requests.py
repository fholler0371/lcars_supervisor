import aiohttp
import time
import aioretry

from models.msg import MsgBase, MsgAppList, MsgGetHostName, MsgRelay
from models.basic import StringList
from models.network import Hostname
from corelib.aio_property import aproperty


class RetryException(BaseException):
    pass 

MAX_RETRY = 7
def retry_policy(info: aioretry.RetryInfo) -> aioretry.RetryPolicyStrategy:
    return info.fails > MAX_RETRY, (2 ** info.fails) * 0.1

class LcarsRequests:
    def __init__(self, core: object) -> None:
        self.__core = core
        self.__app_list_valid = 0
        self.__app_list = []
        self.__hostname = None
        self.session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=1,sock_read=5)
        self.session_connector = aiohttp.TCPConnector(verify_ssl=False)
    
    async def msg(self, app: str, msg: MsgBase, host: str|None = None, host_check=True) -> dict:
        if msg.data is None:
            msg.data = {}
        if host is None and host_check:
            if '.' in app:
                ...
            else:
                for z_full in await self.app_list:
                    #self.__core.log.critical(z_full)
                    if app in z_full:
                        z_host, _ = z_full.split('.')
                        if z_host != await self.hostname:
                            msg = MsgRelay(app=app, data=msg.data.model_dump(), host=z_host)
                            app = 'gateway'
                        break
                    else:
                        self.__app_list_valid = 0
        if host is None:
            url= f"http://{app}:1235/com/1/{msg.path}"
            header = {'X-Auth': self.__core._local_keys.local}
            data = msg.data.copy()
            data['type'] = msg.type
            if hasattr(msg, 'app'):
                data['dest_app'] = msg.app
            if hasattr(msg, 'host'):
                data['dest_host'] = msg.host
        else:
            url = f"http://{self.__core._local_keys.ip[host]}:1235/com/1/{msg.path}"
            header = {'X-Auth': getattr(self.__core._local_keys, host)}
            data = msg.data.copy()
            data['type'] = msg.type
        self.__core.log.info(url)
        self.__core.log.info(header)
        self.__core.log.info(data)
        ret = await self._post_retry(url, header=header, data=data)
        self.__core.log.info(f'{ret} {url}')
        return ret

    @aioretry.retry(retry_policy)
    async def _post_retry(self, url: str, header:str =None, data: dict =None) -> dict:
        self.__core.log.info('run post')
        header = {} if header is None else header
        data = {} if data is None else data
        async with aiohttp.ClientSession(headers=header, timeout=self.session_timeout) as session: #, connector=self.session_connector
            async with session.post(url, json=data) as response:
                self.__core.log.info(response)
                if response.status != 200:
                    raise RetryException()
                try:
                    return await response.json()
                except:
                    ...
                try:
                    return await response.text()
                except:
                    ...
                return await response.read()
            
    @aproperty
    async def app_list(self):
        if self.__app_list_valid < time.time():
            resp = await self.msg(app='gateway', msg=MsgAppList(), host_check=False)
            if resp is not None:
                data = StringList.model_validate(resp)
                self.__app_list = data.data
                self.__app_list_valid = time.time() + self.__core.random(600)
        return self.__app_list

    @aproperty
    async def hostname(self):
        if self.__hostname is None:
            #self.__core.log.critical(f'start {time.time()}')
            try:
                resp = await self.msg(app='gateway', msg=MsgGetHostName(), host_check=False)
                #self.__core.log.critical(resp)
            except:
                ...
            #self.__core.log.critical(f'end {time.time()}')
            #data = Hostname.model_validate(resp)
            self.__hostname = resp['hostname']
        return self.__hostname
