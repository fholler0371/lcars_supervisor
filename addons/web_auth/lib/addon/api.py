from aiohttp import web
import time
from netaddr import IPAddress, IPNetwork
try:
    import bcrypt
except Exception as e:
    print(e, flush=True)
import json
import pathlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import aiofiles
import jwt

from corelib import BaseObj, Core
import aiotomllib
import aiodatabase
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.network import IpData
import cryptlib

from addon.models import UserLogin, LoginResponce, CodeData, TokenByCode, OpenId
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
        self._code_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/code.sqlite3")
        self._code_db.add_table(db_settings.Code())
        self._acl = None
        self._local_ip_valid = 0
        self.rsa_private_key = None
        
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
            ldata.roles = ((await self._users_db.table('users').exec('get_role_sec_by_id', {'id': ldata.user_id}))['roles_sec']
                           if ldata.secure else
                           (await self._users_db.table('users').exec('get_role_by_id', {'id': ldata.user_id}))['roles'])

    async def get_login_token(self, ldata: UserLogin) -> None:
        data = json.dumps({'t': int(time.time()) + (604_800 if ldata.secure else 28_000), 'u':ldata.user_id_s})
        return self.core.com._aes.encrypt(data)
    
    async def get_code(self, cd: CodeData) -> str:
        try:
            await self._code_db.table('codes').exec('delete', {'timestamp': int(time.time()-10)})
            code = cryptlib.key_gen(32)
            await self._code_db.table('codes').exec('insert', {'code': code, 
                                                               'data': cd.model_dump_json(), 
                                                               'timestamp': int(time.time())})
            return code
        except Exception as e:
            self.core.log.error(e)
    
    async def doLogin(self, rd:HttpRequestData, ldata: UserLogin) -> tuple:
        ldata.secure = await self.check_ip(ldata.ip) # prüfen der ip
        await self.check_app(ldata)
        await self.check_user_login(ldata)
        if ldata.valid:
            cd = CodeData.model_validate(ldata.model_dump())
            lr = LoginResponce(login_token=await self.get_login_token(ldata),
                               redirect_url=f"{ldata.callback}?code={await self.get_code(cd)}&state={ldata.state}")
            return (True, web.json_response(lr.model_dump()))
        return (True, web.json_response(SendOk(ok=False).model_dump()))
    
    async def get_ldata_by_token(self, tc:TokenByCode) -> UserLogin:
        try:
            if tc.code:
                await self._code_db.table('codes').exec('delete', {'timestamp': int(time.time()-10)})
                data = await self._code_db.table('codes').exec('data', {'code': tc.code})
                if data:
                    return UserLogin.model_validate_json(data['data'])
        except Exception as e:
            self.core.log.error(e)

    async def validate_oauth_app(self, ldata: UserLogin, tc:TokenByCode):
        try:
            o_data = await self._apps_db.table('oauth').exec('get_client_data', {'app_id': ldata.app_id})
            if self.core.com._aes.decrypt(o_data['secret']) != tc.secret or o_data['callback'] != tc.callback:
                ldata.app_id = -1
            else:
                a_data = await self._apps_db.table('app').exec('get_app_by_id', {'id': ldata.app_id})
                ldata.app_name = a_data['name']
        except Exception as e:
            self.core.log.error(e)
    
    async def craete_token(self, request: HttpRequestData, ldata: UserLogin) -> None:
        try:
            cur_time = int(time.time())
            exp_time = cur_time + 900
            if ldata.secure:
                exp_time = cur_time + 10800
            openid = OpenId(user_id_s= ldata.user_id_s,
                            iss= f"{request.scheme}://{request.host}/auth",
                            iat= cur_time,
                            exp= exp_time,
                            aud= f"{request.scheme}://{request.host}/api")
            if 'name' in ldata.scope:
                user_data = await self._users_db.table('users').exec('get_name_by_id', {'id': ldata.user_id})
                if user_data is not None:
                    openid.name = user_data['name']
            if 'role' in ldata.scope:
                openid.role = ldata.roles
            openid_token = jwt.encode(openid.model_dump(exclude_none=True), self.rsa_private_key, algorithm='RS256')
            self.core.log.debug(openid_token)
        except Exception as e:
            self.core.log.error(e)
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'do_login':
                msg = HttpMsgData.model_validate(rd.data)
                msg2 = HttpRequestData.model_validate(msg.data)
                ldata = UserLogin.model_validate_json(msg2.data)
                ldata.ip = msg2.ip
                return await self.doLogin(rd, ldata)
            case 'token':
                msg = HttpMsgData.model_validate(rd.data)
                msg2 = HttpRequestData.model_validate(msg.data)
                tc = TokenByCode.model_validate(msg2.data)
                ldata = await self.get_ldata_by_token(tc)
                if ldata is None:
                    return (True, web.Response(status=403))
                await self.validate_oauth_app(ldata, tc)
                if ldata.valid:
                    await self.craete_token(msg2, ldata)
                self.core.log.debug(msg2)
                self.core.log.debug(ldata)
    
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        await self._code_db.setup()
        
    async def _astart(self):
        self.core.log.debug('starte api')
        try:
            self.rsa_private_file = pathlib.Path('/lcars/data/rsa_private.pem')
            self.rsa_public_file = pathlib.Path('/lcars/data/rsa_public.pem')
            if self.rsa_private_file.exists():
                self.core.log.debug('lade rsa keys')
                async with aiofiles.open(str(self.rsa_private_file)) as f:
                    key_data = await f.read()
                    key_data = self.core.com._aes.decrypt(key_data)
                    self.rsa_private_key =  serialization.load_pem_private_key(key_data.encode(), password=None)
            else:
                self.core.log.debug('ertelle rsa keys')
                self.rsa_private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048  
                )
                private_key_pem = self.rsa_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode()
                private_key_pem = self.core.com._aes.encrypt(private_key_pem)
                async with aiofiles.open(str(self.rsa_private_file), 'w') as f:
                    await f.write(private_key_pem)
                public_key = self.rsa_private_key.public_key()
                pem_public = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()
                async with aiofiles.open(str(self.rsa_public_file), 'w') as f:
                    await f.write(pem_public)
        except Exception as e:
            self.core.log.error(e)
