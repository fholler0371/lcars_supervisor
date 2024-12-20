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
import pyotp

from corelib import BaseObj, Core
import aiotomllib
import aiodatabase
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.auth import Moduls
from models.network import IpData
from models.basic import StringList
import cryptlib
import aioauth

from addon.models import UserLogin, LoginResponce, CodeData, TokenByCode, OpenId, TokenResponce, UserLabel, UserPassword, UserMail
import addon.db as db_settings

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._auth = aioauth.Client(self.core)
        self._apps_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/apps.sqlite3")
        self._apps_db.add_table(db_settings.App())
        self._apps_db.add_table(db_settings.Oauth())
        self._users_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/users.sqlite3")
        self._users_db.add_table(db_settings.Users())
        self._pw_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/pw.sqlite3")
        self._pw_db.add_table(db_settings.Pw())
        self._pw_db.add_table(db_settings.Otp())
        self._code_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/code.sqlite3")
        self._code_db.add_table(db_settings.Code())
        self._token_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/token.sqlite3")
        self._token_db.add_table(db_settings.RefreshToken())
        self._scopes_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/scopes.sqlite3")
        self._scopes_db.add_table(db_settings.Scopes())
        self._acl = None
        self._local_ip_valid = 0
        self.rsa_private_key = None
        self._npm_gateway = None
        
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
                if not self._npm_gateway:
                    try:
                        resp = await self.core.web_l.msg_send(HttpMsgData(dest='gateway', type='get_docker_gateway_by_container', data={'container': 'npm'}))
                        if resp:
                            self._npm_gateway = resp['data']
                    except:
                        pass
                if self._npm_gateway == ip:
                    self.core.log.debug('IP6 Aufruf')
                    return False
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
            callback = ldata.callback.split('.')
            if callback[0][-1] == '4':
                callback[0] = callback[0][:-1]
            callback = ".".join(callback)
            app_id = await self._apps_db.table('oauth').exec('get_id_by_clientid_callback', {'clientid': ldata.clientid, 'callback': callback})
            if app_id is not None:
                ldata.app_id = app_id['app_id']

    async def check_user_login(self, ldata: UserLogin) -> None:
        ok = False
        if ldata.login_token:
            try:
                token_data = json.loads(self.core.com._aes.decrypt(ldata.login_token))
                if token_data['t'] < time.time():
                    return
                user = await self._users_db.table('users').exec('get_user_by_user_id', {'user_id': token_data['u']})
                if user is not None:
                    ok = True
            except Exception as e:
                self.core.log.error(e)
        else:            
            user = await self._users_db.table('users').exec('get_user_by_name', {'name': ldata.name})
            self.core.log.error(user)
            if user is not None:
                pw = await self._pw_db.table('pw').exec('get_password_by_id', {'id': user['id']})
                self.core.log.error(pw)
                if pw is not None:
                    ok = bcrypt.checkpw((self.core.com._salt+ldata.password).encode(), pw['password'].encode())
                    self.core.log.error(ok)


        if ok:
            try:
                ldata.user_id = user['id']
                ldata.user_id_s = user['user_id']
                if not ldata.secure and ldata.totp:
                    res = await self._pw_db.table('otp').exec('get', {'id': ldata.user_id})
                    if res:
                        secret = res['otp']
                        otp = pyotp.TOTP(secret)
                        ldata.secure = otp.verify(ldata.totp)
                ldata.roles = ((await self._users_db.table('users').exec('get_role_sec_by_id', {'id': ldata.user_id}))['roles_sec']
                            if ldata.secure else
                            (await self._users_db.table('users').exec('get_role_by_id', {'id': ldata.user_id}))['roles'])
                ldata.apps = ((await self._users_db.table('users').exec('get_app_sec_by_id', {'id': ldata.user_id}))['apps_sec']
                            if ldata.secure else
                            (await self._users_db.table('users').exec('get_app_by_id', {'id': ldata.user_id}))['apps'])
            except Exception as e:
                self.core.log.error(e)

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
        if not ldata.secure:
            ldata.totp = json.loads(rd.data.data['data'])["totp"]
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
            if tc.grant_type == 'code':
                await self._code_db.table('codes').exec('delete', {'timestamp': int(time.time()-10)})
                data = await self._code_db.table('codes').exec('data', {'code': tc.code})
                if data:
                    return UserLogin.model_validate_json(data['data'])
            elif tc.grant_type == 'refresh_token':
                await self._token_db.table('refresh_token').exec('delete', {'timestamp': int(time.time()-604_800)})
                data = await self._token_db.table('refresh_token').exec('data', {'token': tc.code})
                if data:
                    return UserLogin.model_validate_json(data['data'])
        except Exception as e:
            self.core.log.error(e)

    async def validate_oauth_app(self, ldata: UserLogin, tc:TokenByCode):
        try:
            callback = tc.callback.split('.')
            if callback[0][-1] == '4':
                callback[0] = callback[0][:-1]
            callback = ".".join(callback)
            o_data = await self._apps_db.table('oauth').exec('get_client_data', {'app_id': ldata.app_id})
            if tc.grant_type not in ['code', 'refresh_token']:
                ldata.app_id = -1
            elif tc.grant_type == 'code' and (self.core.com._aes.decrypt(o_data['secret']) != tc.secret or o_data['callback'] != callback):
                ldata.app_id = -1
            elif tc.grant_type == 'refresh_token' and (self.core.com._aes.decrypt(o_data['secret']) != tc.secret):
                ldata.app_id = -1
            else:
                a_data = await self._apps_db.table('app').exec('get_app_by_id', {'id': ldata.app_id})
                ldata.app_name = a_data['name']
        except Exception as e:
            self.core.log.error(e)
    
    async def craete_token(self, request: HttpRequestData, ldata: UserLogin) -> None:
        try:
            cur_time = int(time.time())
            exp_time = 900
            if ldata.secure:
                exp_time = 10_800
            openid = OpenId(user_id_s= ldata.user_id_s,
                            iss= f"{request.scheme}://{request.host}/auth",
                            iat= cur_time,
                            exp= exp_time+cur_time,
                            aud= f"{request.scheme}://{request.host}/api",
                            loc= 1 if ldata.secure else 0)
            if 'name' in ldata.scope:
                user_data = await self._users_db.table('users').exec('get_name_by_id', {'id': ldata.user_id})
                if user_data is not None:
                    if user_data['label']:
                        openid.name = user_data['label']
                    else:
                        openid.name = user_data['name']
            if 'role' in ldata.scope.split(' '):
                openid.role = ldata.roles
            if 'app' in ldata.scope.split(' '):
                openid.app = ldata.apps
            openid_token = jwt.encode(openid.model_dump(exclude_none=True), self.rsa_private_key, algorithm='RS256')
            #refresh_token
            await self._token_db.table('refresh_token').exec('delete', {'timestamp': int(time.time()-604_800)})
            refresh_token = cryptlib.key_gen(64)
            await self._token_db.table('refresh_token').exec('insert', {'token': refresh_token, 
                                                                        'data': ldata.model_dump_json(), 
                                                                        'timestamp': int(time.time())})
            token = TokenResponce(access_token=openid_token,
                                  expires_in = exp_time,
                                  refresh_token = refresh_token)
            return (True, web.json_response(token.model_dump()))
        except Exception as e:
            self.core.log.error(e)
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        #prüfen ob einträge für allgemeine auth handler ist
        auth_resp = await self._auth.handler(request, rd)
        if auth_resp[0]:
            return auth_resp
        #call für dieses Modul
        match '/'.join(rd.path):
            case 'do_login':
                msg = HttpMsgData.model_validate(rd.data)
                msg2 = HttpRequestData.model_validate(msg.data)
                ldata = UserLogin.model_validate_json(msg2.data)
                ldata.ip = msg2.ip
                return await self.doLogin(rd, ldata)
            case 'do_auto_login':
                msg = HttpMsgData.model_validate(rd.data)
                msg2 = HttpRequestData.model_validate(msg.data)
                ldata = UserLogin.model_validate_json(msg2.data)
                ldata.ip = msg2.ip
                return await self.doLogin(rd, ldata)
            case 'token':
                self.core.log.debug(rd.data)
                msg = HttpMsgData.model_validate(rd.data)
                msg2 = HttpRequestData.model_validate(msg.data)
                self.core.log.debug(msg2.data)
                tc = TokenByCode.model_validate(msg2.data)
                self.core.log.debug(tc)
                ldata = await self.get_ldata_by_token(tc)
                if ldata is None:
                    return (True, web.Response(status=403))
                await self.validate_oauth_app(ldata, tc)
                if ldata.valid:
                    return await self.craete_token(msg2, ldata)
            case 'get_allowed_moduls':
                try:
                    rd = HttpMsgData.model_validate(rd.data)
                    rd = HttpRequestData.model_validate(rd.data)
                except:
                    pass
                if rd.open_id and ('user' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = Moduls()
                    if 'user' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*':
                        data.append({'mod': 'auth_user', 'src': '/auth/js/mod/auth_user'})
                    if 'user_sec' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*':
                        data.append({'mod': 'auth_user_sec', 'src': '/auth/js/mod/auth_user_sec'})
                    if 'user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*':
                        data.append({'mod': 'auth_admin', 'src': '/auth/js/mod/auth_admin'})
                    return (True, web.json_response(data.model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'user/get_label':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    user = await self._users_db.table('users').exec('get_id_by_user_id', {'user_id': rd.open_id['sub']})
                    name_data = await self._users_db.table('users').exec('get_name_by_id', {'id': user['id']})
                    label = name_data['name']
                    if name_data['label']:
                        label = name_data['label']
                    return (True, web.json_response({'ok': True, 'label': label}))
            case 'user/set_label': 
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    label_data = UserLabel.model_validate_json(rd.data)
                    await self._users_db.table('users').exec('update_label_by_user_id', {'user_id': rd.open_id['sub'], 'label':label_data.label})
                    return (True, web.json_response(SendOk().model_dump()))
            case 'user/set_password': 
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    password_data = UserPassword.model_validate_json(rd.data)
                    if password_data.valid:
                        user = await self._users_db.table('users').exec('get_id_by_user_id', {'user_id': rd.open_id['sub']})
                        pw = await self._pw_db.table('pw').exec('get_password_by_id', {'id': user['id']})
                        if bcrypt.checkpw((self.core.com._salt+password_data.password).encode(), pw['password'].encode()):
                            pw_hash = bcrypt.hashpw((self.core.com._salt+password_data.password_new).encode(), bcrypt.gensalt()).decode()
                            await self._pw_db.table('pw').exec('update', {'id': user['id'], 'password': pw_hash})
                            return (True, web.json_response(SendOk().model_dump()))                
            case 'user/get_mail':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_sec' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    mail_data = await self._users_db.table('users').exec('get_mail_by_user_id', {'user_id': rd.open_id['sub']})
                    mail = ''
                    if mail_data['mail']:
                        mail = mail_data['mail']
                    return (True, web.json_response({'ok': True, 'mail': mail}))
            case 'user/set_mail': 
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_sec' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    mail_data = UserMail.model_validate_json(rd.data)
                    await self._users_db.table('users').exec('update_mail_by_user_id', {'user_id': rd.open_id['sub'], 'mail':mail_data.mail})
                    return (True, web.json_response(SendOk().model_dump()))
            case 'user/get_totp':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_sec' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    user = await self._users_db.table('users').exec('get_id_by_user_id', {'user_id': rd.open_id['sub']})
                    if user:
                        token = pyotp.random_base32()
                        _project =  (await aiotomllib.loader(self.core.path.config / 'secret.toml')).get('project', '')
                        otp = await self._pw_db.table('otp').exec('get', {'id': user['id']})
                        if otp:
                            await self._pw_db.table('otp').exec('update', {'id': user['id'], 'otp': token})
                        else:
                            await self._pw_db.table('otp').exec('insert', {'id': user['id'], 'otp': token})
                        uri = pyotp.totp.TOTP(token).provisioning_uri(name=rd.open_id['name'], issuer_name=_project)

                        return (True, web.json_response({'ok': True, 'otp': token, 'uri': uri}))
            case 'admin/get':
                self.core.log.debug('get user list')
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    names = await self._users_db.table('users').exec('get_names')
                    self.core.log.critical(names)
                    out = []
                    if names:
                        for entry in names:
                            out.append(entry['name'])
                    out = StringList(data=out)
                    return (True, web.json_response({'ok': True, 'data': out.model_dump()}))
            case 'admin/get_user':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = json.loads(rd.data)
                    id = await self._users_db.table('users').exec('get_user_by_name', {'name': data['name']})
                    resp = await self._users_db.table('users').exec('get_name_by_id', {'id': id['id']})
                    rec = {'label': resp['label'], 'ok':True, 'rights_avail': [], 'rights': [], 'rights_sec': []}
                    if not rec['label']:
                        rec['label'] = resp['name']
                    resp = await self._users_db.table('users').exec('get_mail_by_user_id', {'user_id': id['user_id']})
                    rec['mail'] = resp['mail'] if resp['mail'] else ''
                    if (resp := await self._scopes_db.table('scopes').exec('get_all', {'timestamp': int(time.time() - 7 * 86400)})):
                        for entry in resp:
                            rec['rights_avail'].append(entry['label'])
                    if (resp := await self._users_db.table('users').exec('get_app_by_id', {'id': id['id']})) and resp['apps']:
                        for entry in resp.get('apps', '').split(' '):
                            rec['rights'].append(entry)
                    if (resp := await self._users_db.table('users').exec('get_app_sec_by_id', {'id': id['id']})) and resp['apps_sec']:
                        self.core.log.critical(resp)
                        for entry in resp.get('apps_sec', '').split(' '):
                            rec['rights_sec'].append(entry)
                    return (True, web.json_response(rec))
            case 'admin/user_add':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = json.loads(rd.data)
                    id = await self._users_db.table('users').exec('get_user_by_name', {'name': data['name']})
                    if id:
                        return (True, web.json_response({'ok': False}))
                    else:
                        user_id_s = cryptlib.key_gen(16)
                        await self._users_db.table('users').exec('insert', {'user_id': user_id_s, 'name': data['name']})
                        return (True, web.json_response({'ok': True}))
            case 'admin/user_del':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = json.loads(rd.data)
                    await self._users_db.table('users').exec('delete', {'name': data['name']})
                    return (True, web.json_response({'ok': True}))
            case 'admin/user_edit':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = json.loads(rd.data)
                    id = await self._users_db.table('users').exec('get_user_by_name', {'name': data['name']})
                    await self._users_db.table('users').exec('update_label_by_user_id', {'user_id': id['user_id'], 'label': data['label']})
                    await self._users_db.table('users').exec('update_mail_by_user_id', {'user_id': id['user_id'], 'mail': data['mail']})
                    return (True, web.json_response({'ok': True}))
            case 'admin/set_password':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = json.loads(rd.data)
                    id = await self._users_db.table('users').exec('get_user_by_name', {'name': data['name']})
                    try:
                        self.core.log.error(self.core.com._salt+data['password'])
                        
                        pw_hash = bcrypt.hashpw((self.core.com._salt+data['password']).encode(), bcrypt.gensalt()).decode()
                        result = await self._pw_db.table('pw').exec('get_password_by_id', {'id': id['id']})
                        self.core.log.error(result)
                        if result is None:
                            await self._pw_db.table('pw').exec('insert', {'id': id['id'], 'password': pw_hash})
                        else:
                            await self._pw_db.table('pw').exec('update', {'id': id['id'], 'password': pw_hash})
                    except Exception as e:
                        self.core.log.error(repr(e))
                    return (True, web.json_response({'ok': True}))
            case 'admin/set_apps':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = json.loads(rd.data)
                    id = await self._users_db.table('users').exec('get_user_by_name', {'name': data['name']})
                    await self._users_db.table('users').exec('update_apps_by_user_id', {'user_id': id['user_id'], 'apps': " ".join(data['apps']),
                                                                                        'apps_sec': " ".join(data['apps_sec'])})
                return (True, web.json_response({'ok': True}))
            case 'admin/mfa':
                rd = HttpMsgData.model_validate(rd.data)
                rd = HttpRequestData.model_validate(rd.data)
                if rd.open_id and ('user_admin' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data = json.loads(rd.data)
                    id = await self._users_db.table('users').exec('get_user_by_name', {'name': data['name']})
                    if id:
                        token = pyotp.random_base32()
                        _project =  (await aiotomllib.loader(self.core.path.config / 'secret.toml')).get('project', '')
                        otp = await self._pw_db.table('otp').exec('get', {'id': id['id']})
                        if otp:
                            await self._pw_db.table('otp').exec('update', {'id': id['id'], 'otp': token})
                        else:
                            await self._pw_db.table('otp').exec('insert', {'id': id['id'], 'otp': token})
                return (True, web.json_response({'ok': True, 'token': token}))
            case _:
                self.core.log.critical('/'.join(rd.path))
    
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        await self._code_db.setup()
        await self._token_db.setup()
        await self._pw_db.setup()
        await self._scopes_db.setup()
        
    async def set_scopes(self, scopes):
        for entry in scopes:
            resp = await self._scopes_db.table('scopes').exec('get_timestamp', {'label': entry})
            if resp:
                await self._scopes_db.table('scopes').exec('update', {'label': entry, 'timestamp': int(time.time())})
            else:
                await self._scopes_db.table('scopes').exec('insert', {'label': entry, 'timestamp': int(time.time())})
        
    async def own_scopes(self):
        self.core.log.debug('scopes aktualiesieren')
        await self.core.call_random(12*3600, self.own_scopes)
        await self.set_scopes(['user', 'user_sec', 'user_admin'])
            
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.own_scopes)
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
                    key_size=2048,
                    alg='RSA-OAEP-256', 
                    use='enc', 
                    kid='12345'
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
