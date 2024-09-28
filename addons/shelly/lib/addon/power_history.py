import tomllib
import aiohttp

from datetime import datetime as dt
from os import walk
import time
import asyncio

import aiodatabase

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk

import addon.db as db_settings

class PowerHistory(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        self.sem = asyncio.Semaphore(4)
        self.history_lock = {}
                
    async def do_check_loop(self):
        await self.core.call_random(3600*6, self.do_check_loop)
        self.core.log.debug('starte history download')
        try:
            with open('/lcars/data/devices.toml', 'rb') as f:
                devices = tomllib.load(f)
            for name, data in devices.items():
                match data.get('type'):
                    case 'Pro3EM':
                        #self.core.log.debug(data)
                        await self.core.call_random(60,self.do_get_emdata, name, data)
        except Exception as e:
            self.core.log.error(e)

    async def do_get_emdata_update(self, name, data, url, db):
        count_new = 0
        count_found = 0
        count_line = 0
        async with aiohttp.ClientSession() as session: 
            #add_keys=true&ts=1726853363&end_ts=1726856963
            #add_keys=true&ts={last_ts}&end_ts={now_ts}
            self.core.log.debug(f'url: {url}')
            async with session.get(url) as resp:
            #self.core.log.debug(f'status: {resp.status} / {resp.content_length}')
                if resp.status == 200:
                    csv_lines = (await resp.text()).split('\n')
                    number_of_lines = len(csv_lines)
                    self.core.log.debug(f'{number_of_lines} Zeilen geladen')
                    csv_header = csv_lines[0].split(',')
                    csv_lines = csv_lines[1:]
                    start_time = time.time()
                    for line in csv_lines:
                        count_line += 1
                        if line != "": # and count_found < 250:
                            values = line.split(',')
                            tstamp = int(values[0])
                            for idx, label in enumerate(csv_header[1:]):
                                try:
                                    db_id = await db.table('history').exec('get_id', {'tstamp': tstamp, 'label': label})
                                    if db_id:
                                        #await db.table('history').exec('update', {'value': values[1+idx], 'id': db_id['id']})
                                        count_found += 1
                                    else:
                                        await db.table('history').exec('insert', {'tstamp': tstamp, 'label': label, 'value': values[1+idx]})
                                        count_new += 1
                                    if (count_new+count_found) % 1000 == 0 or time.time()-start_time > 300:
                                        start_time = time.time()
                                        self.core.log.debug(f'{count_new} neue Einträge / {count_found} alte Einträge / {count_line} Zeilen / {name} / {(count_line/number_of_lines):.2%}')
    #                                    self.core.log.debug(idx)
    #                                    self.core.log.debug(label)
                                except Exception as e:
                                    self.core.log.error(repr(e))
                    self.core.log.debug(f'{count_new} neue Einträge')
                elif resp.status == 400:
                    self.core.log.debug("es liegen keine Daten vor")
                else:
                    self.core.log.debug(resp.status)
            
    async def do_get_emdata(self, name, data):
        self.core.log.debug(f'get data von {name}')
        if name not in self.history_lock:
            self.history_lock[name] = asyncio.Lock()
        db = self._apps_db = aiodatabase.DB(f"sqlite:///{self.core.path.data}/power_history_{name}.sqlite3") 
        db.add_table(db_settings.PowerHist())
        await db.setup()
        count_new = 0
        count_found = 0
        count_line = 0
        try:
            async with self.history_lock[name]:
                try:
                    last_ts = (await db.table('history').exec('get_last'))['tstamp'] - (3600*12)
                    now_ts = int(time.time())
                    if (now_ts - 7 * 86400) > last_ts:
                        now_ts = last_ts + 7 * 86400
                    url = f'http://{data["ip"]}/emdata/0/data.csv?add_keys=true&ts={last_ts}&end_ts={now_ts}'
                except:
                    now_ts = int(time.time())
                    last_ts = now_ts - 7 * 86400
                    url = f'http://{data["ip"]}/emdata/0/data.csv?add_keys=true&ts={last_ts}&end_ts={now_ts}'
                await self.do_get_emdata_update(name, data, url, db)
        except Exception as e:
            self.core.log.error(repr(e))
        try:
            async with self.history_lock[name]:
                now_ts = (await db.table('history').exec('get_first'))['tstamp']
                last_ts = now_ts - 7 * 86400
                url = f'http://{data["ip"]}/emdata/0/data.csv?add_keys=true&ts={last_ts}&end_ts={now_ts}'
                await self.do_get_emdata_update(name, data, url, db)
        except Exception as e:
            self.core.log.error(repr(e))
        
    async def do_month(self):
        rem_folder = f'month/{await self.core.web_l.hostname}'
        idx = str(dt.today().month)
        idx_file = f'{rem_folder}/index'
        rem_folder = f'{rem_folder}/{idx}'
        await self.do_scan(idx, idx_file, rem_folder)
        
    async def do_backup(self):
        await self.core.call_random(3600, self.do_backup)
        self.core.log.debug('backup loop')
        await self.do_day()
        await self.do_month()
        
    async def _astart(self):
        self.core.log.debug('starte history download loop')
        await self.core.call_random(300, self.do_check_loop) 