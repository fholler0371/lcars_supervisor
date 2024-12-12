import aiohttp
import time
import aioretry

from models.msg import MsgBase, MsgAppList
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
        self.session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=1,sock_read=5)
        self.session_connector = aiohttp.TCPConnector(verify_ssl=False)
    
    async def msg(self, app: str, msg: MsgBase, host: str|None = None, host_check=True) -> dict:
        if msg.data is None:
            msg.data = {}
        if host is None and host_check:
            self.__core.log.critical('xxx')
            self.__core.log.critical(app)
            _app = await self.app_list
            self.__core.log.critical(_app)
        if host is None:
            url= f"http://{app}:1234/com/1/{msg.path}"
            header = {'X-Auth': self.__core._local_keys.local}
            data = msg.data.copy()
            data['type'] = msg.type
        else:
            url = f"http://{self.__core._local_keys.ip[host]}:1235/com/1/{msg.path}"
            header = {'X-Auth': getattr(self.__core._local_keys, host)}
            data = msg.data.copy()
            data['type'] = msg.type
        ret = await self._post_retry(url, header=header, data=data)
        self.__core.log.info(ret)
        return ret

    @aioretry.retry(retry_policy)
    async def _post_retry(self, url: str, header:str =None, data: dict =None) -> dict:
        header = {} if header is None else header
        data = {} if data is None else data
        async with aiohttp.ClientSession(headers=header, timeout=self.session_timeout, connector=self.session_connector) as session:
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    raise 
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
            self.__core.log.info(resp)
        #     if resp is not None:
        #         data = StringList.model_validate(resp)
        #         self._app_list = data.data
        #         self._app_list_valid = time.time() + self.core.random(600)
        return self.__app_list
