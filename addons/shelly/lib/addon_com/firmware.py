import tomllib
import aiohttp

from datetime import datetime as dt
from os import walk
import os

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk

class Firmwarcheck(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
                
    async def do_check_loop(self):
        await self.core.call_random(24*3600, self.do_check_loop)
        self.core.log.debug('starte firmwarecheck')
        try:
            with open('/lcars/data/devices.toml', 'rb') as f:
                devices = tomllib.load(f)
            for name, data in devices.items():
                match data.get('gen'):
                    case 2:
                        await self.do_check_gen2(name, data)
        except Exception as e:
            self.core.log.error(e)
            
    async def do_check_gen2(self, name, data):
        self.core.log.debug(f'check {name}')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://{data["ip"]}/rpc/Shelly.CheckForUpdate') as resp:
                    if resp.status == 200:
                        firmware_state = await resp.json()
                        if 'stable' in firmware_state:
                            self.core.log.debug(f"neue stabile Version {firmware_state['stable']['version']}")
                            async with session.get(f'http://{data["ip"]}/rpc/Shelly.Update?stage=stable') as resp:
                                if resp.status == 200:
                                    self.core.log.debug('Update gestartet')
                                else:
                                    self.core.log.debug(f'Fehler beim Update start {resp.status}')
        except Exception as e:
            self.core.log.error(e)

        
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
        self.core.log.debug('starte firmwarecheck loop')
        await self.core.call_random(30, self.do_check_loop)