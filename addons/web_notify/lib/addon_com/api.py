from aiohttp import web
import tomllib
import json

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.auth import Moduls
from models.basic import ListOfDict, Dict


class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
                
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        #prüfen ob einträge für allgemeine auth handler ist
        self.core.log.debug('get call')
        #auth_resp = await self._auth.handler(request, rd)
        #if auth_resp[0]:
        #    return auth_resp
        #call für dieses Modul
        match '/'.join(rd.path):
            case 'get_allowed_moduls':
                try:
                    rd = HttpMsgData.model_validate(rd.data)
                    rd = HttpRequestData.model_validate(rd.data)
                except:
                    pass
                data = Moduls()
                if rd.open_id and ('notify' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data.append({'mod': 'notify_list', 'src': '/notify/js/mod/notify_list'})
                return (True, web.json_response(data.model_dump()))
            case 'notify/get_list':
                self.core.log.debug('Ask for List')
                bc = rd.data.data
                if bc['open_id'] and ('notify' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    resp = await self.core.com._msg_db.table('message').exec('get_all')
                    apps = await self.core.com._apps_db.table('apps').exec('get_all')
                    if resp is not None:
                        for entry in resp:
                            for app in apps:
                                if app['id'] == entry['app']:
                                    entry['app_icon'] = app['icon']
                                    entry['app_name'] = app['label']
                        data = ListOfDict(data=resp)
                        return (True, web.json_response(SendOk(data=data.model_dump()).model_dump()))
                    else:
                        return (True, web.json_response(SendOk(data=[]).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'notify/remove':
                self.core.log.debug('Remove')
                bc = rd.data.data
                if bc['open_id'] and ('notify' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    data = json.loads(bc['data'])
                    await self.core.com._msg_db.table('message').exec('delete', {'md5': data['md5']})
                    return (True, web.json_response(SendOk().model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case _:
                self.core.log.critical('/'.join(rd.path))
    
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        try:
            await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        except Exception as e:
            self.core.log.critical(repr(e))
        self.core.log.debug('Initaliesiere api done')
        
    async def _astart(self):
        self.core.log.debug('starte api')
