from aiohttp import web
from datetime import datetime
from asyncio import Lock
import time
import json

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
            case 'messages/budgets':
                resp = await self._budget_db.table('budgets').exec('get_with_order')
                out = []
                if resp:
                    for entry in resp:
                        rec = {'id': entry['id']}
                        rec['start'] = entry['start']
                        rec['end'] = entry['end']
                        rec['amount'] = entry['amount'] / 100
                        rec['category'] = entry['category']
                        out.append(rec)
                resp = await self._budget_db.table('category').exec('get_all')
                if resp:
                    for entry in out:
                        for cat in resp:
                            if entry['category'] == cat['id']:
                                  entry['category'] = cat['label']
                                  continue    
                out = sorted(out, key = lambda y: y['category'])                 
                out = sorted(out, key = lambda y: y['end'], reverse=True)                 
                out = ListOfDict(data=out)
                return (True, web.json_response(out.model_dump()))
            case 'messages/budget_edit':
                data = rd.data.data
                resp = await self._budget_db.table('category').exec('get_all')
                for cat in resp:
                    if data['category'] == cat['label']:
                        data['category'] = cat['id']
                    continue
                await self._budget_db.table('budgets').exec('edit', {'category': data['category'], 'start': data['start'], 
                                                            'end': data['end'], 'amount': int(data['amount'] * 100), 'id': data['id']})
                self._valid = 0
                return (True, web.json_response({}))
            case 'messages/budget_new':
                resp = await self._budget_db.table('budgets').exec('id_new')
                if resp:
                      return (False, web.json_response({}))
                await self._budget_db.table('budgets').exec('add_new', {'category': 1, 'start': '2000-01-01', 'end': '2000-01-01', 'amount': 0})
                resp = await self._budget_db.table('budgets').exec('id_new')
                rec = {'id': resp['id'], 'category': 1, 'start': '2000-01-01', 'end': '2000-01-01', 'amount': 0}
                resp = await self._budget_db.table('category').exec('get_all')
                for cat in resp:
                    if rec['category'] == cat['id']:
                        rec['category'] = cat['label']
                    continue
                self._valid = 0
                out = Dict(data=rec)
                return (True, web.json_response(out.model_dump()))
            case 'messages/buy_get':
                out = {'categories': [], 'names': []}
                buy_data = await self._budget_db.table('bought').exec('get_500')
                categories = await self._budget_db.table('category').exec('get_all')
                for category in categories:
                    out['categories'].append(category['label'])
                out['categories'] = sorted(out['categories'], key = lambda y: y)
                for entry in buy_data:
                    entry['amount'] = entry['amount'] / 100
                    if entry['name'] not in out['names']:
                        out['names'].append(entry['name'])
                    for category in categories:
                        if entry['category'] == category['id']:
                            entry['category'] = category['label']
                            continue
                food_data = await self._food_db.table('bought').exec('get_500')
                for entry in food_data:
                    if entry['name'] not in out['names']:
                        out['names'].append(entry['name'])
                    entry['amount'] = entry['amount'] / 100
                    entry['category'] = self.food_label
                    entry['id'] += 1_000_000
                    buy_data.append(entry)
                out['names'] = sorted(out['names'], key = lambda y: y)
                buy_data = sorted(buy_data, key = lambda y: y['date'], reverse=True)
                while len(buy_data) > 500:
                    buy_data.pop()                    
                out['list'] = buy_data
                out = Dict(data=out)
                return (True, web.json_response(out.model_dump()))
            case 'messages/buy_edit':
                data = json.loads(rd.data.data)
                if data['id'] > 0:
                    db_old = 0 if data['id'] < 1_000_000 else 1
                    db_new = 1 if data['category'] == self.food_label else 0
                    if db_old == db_new:
                        if db_old == 0:
                            for category in (await self._budget_db.table('category').exec('get_all')):
                                if category['label'] == data['category']:
                                    _category = category['id']
                                    continue
                            await self._budget_db.table('bought').exec('edit', {'id': data['id'], 'date': data['date'], 'category': _category,
                                                                                  'name': data['name'], 'amount': int(data['amount'] * 100), 'count': data['count']})
                        else: # db_new
                            await self._food_db.table('bought').exec('edit', {'id': data['id'] - 1_000_000, 'date': data['date'],
                                                                                'name': data['name'], 'amount': int(data['amount'] * 100), 'count': data['count']})
                    else: #delete
                        if db_old == 0:
                            self.core.log.error({'id': data['id']})
                            await self._budget_db.table('bought').exec('delete', {'id': data['id']})
                            self.core.log.error({'id': data['id']})
                        else: #db_new
                            self.core.log.error({'id': data['id'] - 1_000_000})
                            await self._food_db.table('bought').exec('delete', {'id': data['id'] - 1_000_000})
                            self.core.log.error({'id': data['id'] - 1_000_000})
                        data['id'] = -1
                if data['id'] == -1:
                    db_new = 1 if data['category'] == self.food_label else 0
                    if db_new == 0:
                        for category in await self._budget_db.table('category').exec('get_all'):
                            if category['label'] == data['category']:
                                _category = category['id']
                                continue
                        await self._budget_db.table('bought').exec('add', {'date': data['date'], 'category': _category,
                                                                           'name': data['name'], 'amount': int(data['amount'] * 100), 'count': data['count']})
                        data['id'] = (await self._budget_db.table('bought').exec('get_max_id'))['id']
                    else: #db_new
                        await self._food_db.table('bought').exec('add', {'date': data['date'],
                                                                         'name': data['name'], 'amount': int(data['amount'] * 100), 'count': data['count']})
                        self.core.log.critical(await self._food_db.table('bought').exec('get_max_id'))
                        data['id'] = (await self._food_db.table('bought').exec('get_max_id'))['id'] + 1_000_000
                out = Dict(data=data)    
                self._valid = 0
                return (True, web.json_response(out.model_dump()))        
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