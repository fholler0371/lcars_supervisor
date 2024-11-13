from aiohttp import web
from datetime import datetime
from asyncio import Lock
import time

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpMsgData, HttpHandler, HttpRequestData
from models.basic import ListOfDict, Dict

import aiodatabase
import aiotomllib

import addon.db as db_settings

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._overview = []
        self._valid = 0
        self._recalc_lock = Lock()
        
    async def recalc(self, restart=True):
        def str_to_dt(date):
            return datetime.strptime(date, '%Y-%m-%d')
        
        def date_diff(start, end):
            return (str_to_dt(end) - str_to_dt(start)).days + 1
        
        if restart:
            await self.core.call_random(300, self.recalc)
        if self._valid < time.time():
            async with self._recalc_lock:
                self.core.log.debug('recalc')
                self._overview = []
                if not (res := await self._budget_db.table('category').exec('get_all')):
                    return
                today = datetime.today().strftime('%Y-%m-%d')
                for category in res:
                    category['budget'] = category['out'] = category['last'] = 0
                    try:
                        if not (budgets := await self._budget_db.table('budgets').exec('get_by_category', {'category': category['id']})):
                            continue
                        for budget in budgets:
                            if budget['start'] > today:
                                continue
                            if budget['end'] > today:
                                budget['end'] = today
                            category['per_day'] = budget['amount']*12/365
                            category['budget'] += category['per_day'] * date_diff(budget['start'],budget['end'])
                        if category['label'] == self.food_label:
                            if (out := await self._food_db.table('bought').exec('get_sum')):
                                category['out'] = out['amount']
                        else:
                            if (out := await self._budget_db.table('bought').exec('get_sum', {'category': category['id']})):
                                category['out'] = out['amount']
                        if category['out'] > category['budget']:
                            category['last'] = 1 + int((category['out'] - category['budget']) / category['per_day'])
                    except Exception as e:
                        self.core.log.error(repr(e)) 
                    self._overview.append(category)
                    self._valid = 3 * 3600 + int(time.time())
                
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'messages/relay':
                msg = HttpMsgData.model_validate(rd.data)
                relay_rd = HttpRequestData.model_validate(msg.data)
                return await self.static('/'.join(relay_rd.path))
            case 'messages/get_status':
                active = rd.data.data.get('aktiv', False)
                out = []
                await self.recalc(restart=False)
                for category in self._overview:
                    if active or category['activ'] == 1: 
                        rec = {}
                        rec['category'] = category['label']
                        rec['saldo'] = (category['budget'] - category['out']) / 100
                        rec['payed'] = category['out'] / 100
                        rec['days_info'] = category['days']
                        rec['days'] = category['last']
                        out.append(rec)
                out = ListOfDict(data=out)        
                return (True, web.json_response(out.model_dump()))
            case 'messages/get_categories':
                await self.recalc(restart=False)
                out = []
                for category in self._overview:
                    rec = {}
                    rec['id'] = category['id']
                    rec['label'] = category['label']
                    rec['activ'] = category['activ'] == 1
                    rec['days'] = category['days']
                    out.append(rec)
                out = ListOfDict(data=out)
                return (True, web.json_response(out.model_dump()))
            case 'messages/category_new':
                try:
                    await self._budget_db.table('category').exec('add_new', {'label': 'Neu', 'activ': 1, 'days': 0})
                except:
                    pass
                self._valid = 0
                resp = await self._budget_db.table('category').exec('get_last')
                data = Dict(data=resp)
                return (True, web.json_response(data.model_dump()))
            case 'messages/category_edit':
                data = rd.data.data
                await self._budget_db.table('category').exec('update', {'label': data['label'], 'activ': 1 if data['activ'] else 0, 'days': data['days'], 'id': data['id']})
                self._valid = 0
                return (True, web.json_response({}))
            case _:
                self.core.log.error(rd)
                       
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        conf = await aiotomllib.loader(self.core.path.config / 'config.toml')
        self.food_label = conf['food']['label']
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='lcars_docker'))
        

    async def _astart(self):
        self.core.log.debug('Starte com')
        try:
            self._budget_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/budget.sqlite3")
            self._budget_db.add_table(db_settings.Category())
            self._budget_db.add_table(db_settings.Budgets())
            self._budget_db.add_table(db_settings.Bought())
            self._food_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/food.sqlite3")
            self._food_db.add_table(db_settings.FoodBought())
        except Exception as e:
            self.core.log.error(repr(e))
        await self.core.call_random(30, self.recalc)