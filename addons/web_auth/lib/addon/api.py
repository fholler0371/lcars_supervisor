from aiohttp import web
import time
from netaddr import IPAddress, IPNetwork
try:
    import bcrypt
except Exception as e:
    print(e, flush=True)

from corelib import BaseObj, Core
import aiotomllib
import aiodatabase
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.network import IpData

from addon.models import UserLogin
import addon.db as db_settings

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/apps.sqlite3")
        self._apps_db.add_table(db_settings.App())
        self._apps_db.add_table(db_settings.Oauth())
        self._users_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/users.sqlite3")
        self._users_db.add_table(db_settings.Users())
        self._pw_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/pw.sqlite3")
        self._pw_db.add_table(db_settings.Pw())
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
        
    async def check_app(self, ldata: UserLogin) -> None:
        if ldata.response_type == 'code':
            app_id = await self._apps_db.table('oauth').exec('get_id_by_clientid_callback', {'clientid': ldata.clientid, 'callback': ldata.callback})
            if app_id is not None:
                ldata.app_id = app_id['app_id']

    async def check_user_login(self, ldata: UserLogin) -> None:
        user = await self._users_db.table('users').exec('get_user_by_name', {'name': ldata.name})
        ok = False
        if user is not None:
            pw = await self._pw_db.table('pw').exec('get_password_by_id', {'id': user['id']})
            if pw is not None:
                ok = bcrypt.checkpw((self.core.com._salt+ldata.password).encode(), pw['password'].encode())
        if ok:
            ldata.user_id = user['id']
            ldata.user_id_s = user['user_id']

    async def doLogin(self, rd:HttpRequestData, ldata: UserLogin) -> tuple:
        ldata.secure = await self.check_ip(ldata.ip) # prüfen der ip
        await self.check_app(ldata)
        await self.check_user_login(ldata)
        self.core.log.debug(ldata.valid)
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
