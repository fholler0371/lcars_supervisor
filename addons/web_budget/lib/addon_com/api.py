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
                if rd.open_id and ('budget' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data.append({'mod': 'budget_overview', 'src': '/budget/js/mod/budget_overview'})
                if rd.open_id and ('budget_sec' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data.append({'mod': 'budget_cat', 'src': '/budget/js/mod/budget_cat'})
                    data.append({'mod': 'budget_budgets', 'src': '/budget/js/mod/budget_budgets'})
                if rd.open_id and ('budget' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data.append({'mod': 'budget_buy', 'src': '/budget/js/mod/budget_buy'})
                return (True, web.json_response(data.model_dump()))
            case 'budget/get_status':
                self.core.log.debug('Ask for Status')
                bc = rd.data.data
                if bc['open_id'] and ('budget' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    inaktiv = 'budget_sec' in bc['open_id']['app'].split(' ')
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='get_status', data={'aktiv':inaktiv}))
                    data = ListOfDict.model_validate(resp)
                    return (True, web.json_response(SendOk(data=data.model_dump()).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'category/get_categories':
                self.core.log.debug('Ask for Categories')
                bc = rd.data.data
                if bc['open_id'] and ('budget_sec' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='get_categories'))
                    data = ListOfDict.model_validate(resp)
                    return (True, web.json_response(SendOk(data=data.model_dump()).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'category/category_new':
                bc = rd.data.data
                if bc['open_id'] and ('budget_sec' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='category_new'))
                    data = Dict.model_validate(resp)
                    return (True, web.json_response(SendOk(data=data.model_dump()).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'category/category_edit':
                bc = rd.data.data
                if bc['open_id'] and ('budget_sec' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    data = json.loads(bc['data'])
                    await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='category_edit', data=data))
                    return (True, web.json_response(SendOk().model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'budget/get_all':
                bc = rd.data.data
                if bc['open_id'] and ('budget_sec' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='budgets'))
                    data = ListOfDict.model_validate(resp)
                    return (True, web.json_response(SendOk(data=data.model_dump()).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'budget/budget_edit':
                bc = rd.data.data
                if bc['open_id'] and ('budget_sec' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    data = json.loads(bc['data'])
                    await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='budget_edit', data=data))
                    return (True, web.json_response(SendOk().model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'budget/get_new':
                bc = rd.data.data
                if bc['open_id'] and ('budget_sec' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='budget_new'))
                    if resp:
                        self.core.log.critical(resp)
                        data = Dict.model_validate(resp)
                        self.core.log.critical(data)
                        return (True, web.json_response(SendOk(data=data).model_dump()))
                    else:
                        return (True, web.json_response(SendOk(ok=False).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'budget/buy_get':
                bc = rd.data.data
                if bc['open_id'] and ('budget' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='buy_get'))
                    data = Dict.model_validate(resp)
                    return (True, web.json_response(SendOk(data=data.model_dump()).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'budget/buy_edit':
                self.core.log.debug('Ask Buy Data')
                bc = rd.data.data
                if bc['open_id'] and ('budget' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    resp = await self.core.web_l.msg_send(HttpMsgData(dest='budget', type='buy_edit', data=bc['data']))
                    data = Dict.model_validate(resp)
                    return (True, web.json_response(SendOk(data=data.model_dump()).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case _:
                self.core.log.critical('/'.join(rd.path))
    
    async def add_scopes(self):
        self.core.log.debug('scopes aktualiesieren')
        await self.core.call_random(12*3600 , self.add_scopes) #
        await self.core.web_l.msg_send(HttpMsgData(dest='web_auth', type='set_scopes', data=['budget', 'budget_sec']))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        try:
            await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        except Exception as e:
            self.core.log.critical(repr(e))
        self.core.log.debug('Initaliesiere api done')
        
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.add_scopes)
