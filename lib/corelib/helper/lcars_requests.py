import aiohttp
import aioretry

from models.msg import MsgBase


class RetryException(BaseException):
    pass 

MAX_RETRY = 7
def retry_policy(info: aioretry.RetryInfo) -> aioretry.RetryPolicyStrategy:
    return info.fails > MAX_RETRY, (2 ** info.fails) * 0.1

class LcarsRequests:
    def __init__(self, core: object) -> None:
        self.__core = core
        self.session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=1,sock_read=5)
        self.session_connector = aiohttp.TCPConnector(verify_ssl=False)
    
    async def msg(self, app: str, msg: MsgBase, host: str|None = None) -> dict:
        if msg.data is None:
            msg.data = {}
        if host is None:
            url= ''
            header = {}
            data = {}
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