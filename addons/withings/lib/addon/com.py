from aiohttp import web
from datetime import datetime, timedelta
import aiohttp
import pathlib
import aioyamllib
import time
import tomllib

from corelib import BaseObj, Core
from httplib.models import HttpMsgData, HttpHandler, HttpRequestData, SendOk
from . import models

import aiodatabase

import addon.db as db_settings



class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
        #self._state_name = pathlib.Path('/lcars/data/ip_state.yml')
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        if rd.path[0] == 'messages':
#            msg = HttpMsgData.model_validate(rd.data)
            match rd.path[1]:
                case 'messages/set_token':
                    data = rd.data.data
                    await self.token.set_token(data['token'], data['refresh_token'], data['timeout'])
                    return (True, web.json_response({}))
                case 'sm':
                    data = rd.data.data
                    match rd.path[2]:
                        case 'get_sensor':
                            table, sensor = data['sensor'].split('.')
                            match table:
                                case 'body' | 'heart' | 'temperatur':
                                    res = await self._data_db.table('vital').exec('get_last_by_type', {'type': sensor})
                                    if res:
                                        return (True, web.json_response(SendOk(data={'value': res['value']}).model_dump()))
                                    else:
                                        return (True, web.json_response(SendOk(ok=False).models_dump()))
                                case 'sleep_data':
                                    res = await self._data_db.table('sleep').exec('get_last_by_type', {'type': sensor})
                                    if res:
                                        return (True, web.json_response(SendOk(data={'value': res['value']}).model_dump()))
                                    else:
                                        return (True, web.json_response(SendOk(ok=False).models_dump()))
                                case 'weight_trend':
                                    base_value = 0
                                    avg_value = 0
                                    if res := await self._data_db.table('vital').exec('get_last_by_type', {'type': 'gewicht'}):
                                        base_value = res['value']
                                    self.core.log.critical(sensor.split('_')[1][0])
                                    match sensor.split('_')[1][0]:
                                        case 'm':
                                            _interval = 30 * 86400
                                        case 'q':
                                            _interval = 92 * 86400
                                        case 'y':
                                            _interval = 365 * 86400
                                    if res := await self._data_db.table('vital').exec('get_avg', {'date': int(time.time() - _interval)}):
                                        avg_value = res['value']
                                    return (True, web.json_response(SendOk(data={'value':  base_value - avg_value}).model_dump()))    
                                case 'sum_m' | 'heart_d':
                                    count_letter = sensor.split('_')[-1]
                                    match count_letter:
                                        case 'y':
                                            _sensor = sensor[:-2]
                                            count_days = 365
                                        case 'q':
                                            _sensor = sensor[:-2]
                                            count_days = 92
                                        case 'm':
                                            _sensor = sensor[:-2]
                                            count_days = 31
                                        case 'w':
                                            _sensor = sensor[:-2]
                                            count_days = 7
                                        case _:
                                            _sensor = sensor
                                            count_days = 1
                                    date_max = datetime.today() - timedelta(days=1)
                                    self.core.log.critical(f"{data['sensor']}")
                                    value = 0
                                    date_min = datetime.today() - timedelta(days=count_days)
                                    if res := await self._data_db.table('daily').exec('get_by_date_and_type', {'date_max': date_max.strftime('%Y-%m-%d'),
                                                                                                                   'date_min': date_min.strftime('%Y-%m-%d'),
                                                                                                                   'type': _sensor}):
                                        value = res['value']
                                    self.core.log.critical(res)
                                    self.core.log.critical(_sensor)
                                    self.core.log.critical(date_max)
                                    self.core.log.critical(date_min)
                                    self.core.log.critical(f"{value}")
                                    return (True, web.json_response(SendOk(data={'value':  value }).model_dump())) 
                                case _:
                                    self.core.log.critical(data['sensor'])
                        case 'get_history':
                            _table, _sensor = data['sensor'].split('.')
                            match data['interval']:
                                case 'M':
                                    _interval = 30 * 86400
                                    _days = 30
                                case 'Q':
                                    _interval = 92 * 86400
                                    _days = 92
                                case 'Y':
                                    _interval = 365 * 86400
                                    _days = 365
                                case _:
                                    _interval = 100 * 365 * 86400
                                    _days = 100 * 365
                            match _table:
                                case 'body' | 'heart'| 'temperatur':
                                    res = await self._data_db.table('vital').exec('get_history', {'type': _sensor, 'date': int(time.time() - _interval)})
                                case 'sum_m' | 'heart_d':
                                    res = await self._data_db.table('daily').exec('get_history', {'type': _sensor, 
                                                                                                  'date': (datetime.today() - timedelta(days= _days)).strftime('%Y-%m-%d')})
                                    if res:
                                        for entry in res:
                                            entry['date'] = int((datetime.strptime(entry['date'], '%Y-%m-%d') - datetime(1970,1,1)).total_seconds())
                            if res:
                                return (True, web.json_response(SendOk(data=res).model_dump()))
                            else:
                                return (True, web.json_response(SendOk(ok=False).models_dump()))
                case _:
                     self.core.log.critical(rd)
                        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='lcars_docker'))
        self._data_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/data.sqlite3")
        self._data_db.add_table(db_settings.Vital())
        self._data_db.add_table(db_settings.Daily())
        self._data_db.add_table(db_settings.Sleep())
                   
    async def _astart(self):
        self.core.log.debug('starte com')
        await self._data_db.setup()

    async def _astop(self):
        self.core.log.debug('stoppe com')
