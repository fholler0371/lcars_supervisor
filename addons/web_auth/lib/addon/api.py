from aiohttp import web
import time
from netaddr import IPAddress, IPNetwork

from corelib import BaseObj, Core
import aiotomllib
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.network import IpData

from addon.models import UserLogin


class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._acl = None
        self._local_ip_valid = 0
        
    async def check_ip(self, ip: str) -> None:
        try:
            if self._acl is None:
                ip_data = IpData.model_validate(await self.core.web_l.msg_send(HttpMsgData(dest='avm', type='get_ip')))
                self._acl = [f'{ip_data.ip4}/32']
                self._local_ip_valid = time.time() + 1800
                toml = await aiotomllib.loader(self.core.path.config / 'acl.toml')
                self._acl.append(toml.get('home', ''))
                self._acl.append(toml.get('docker', ''))
            if self._local_ip_valid < time.time():
                ip_data = IpData.model_validate(await self.core.web_l.msg_send(HttpMsgData(dest='avm', type='get_ip')))
                self._acl[0] = f'{ip_data.ip4}/32'
                self._local_ip_valid = time.time() + 1800
            try:
                _ip = IPAddress(ip)
                for acl_ip in self._acl:
                    if _ip in IPNetwork(acl_ip):
                        return True
            except Exception as e:
                self.core.log.error(e)
        except Exception as e:
            self.core.log.error(e)
        return False
        
    async def doLogin(self, rd:HttpRequestData, ldata: UserLogin) -> tuple:
        ldata.secure = await self.check_ip(ldata.ip)
        self.core.log.debug(ldata)

    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'do_login':
                msg = HttpMsgData.model_validate(rd.data)
                msg2 = HttpRequestData.model_validate(msg.data)
                ldata = UserLogin.model_validate_json(msg2.data)
                ldata.ip = msg2.ip
                await self.doLogin(rd, ldata)

    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))

    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(10, self.register_web_app)
