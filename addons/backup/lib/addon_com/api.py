from aiohttp import web
from datetime import datetime as dt
from os import walk
import os

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk

BACKUP_FOLDER = '/lcars/backup'

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def do_scan(self, idx: int, idx_file: str, rem_folder: str):
        for (dirpath, dirnames, filenames) in walk(BACKUP_FOLDER):
            for name in filenames:
                self.core.log.debug(os.path.join(dirpath, name)[len(BACKUP_FOLDER):])
        
        self.core.log.debug(idx_file)   
        self.core.log.debug(rem_folder)
        self.core.log.debug(idx)
       
        
    async def do_day(self):
        rem_folder = f'day/{await self.core.web_l.hostname}'
        idx = str(dt.today().day)
        idx_file = f'{rem_folder}/index'
        rem_folder = f'{rem_folder}/{idx}'
        await self.do_scan(idx, idx_file, rem_folder)
        
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
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.do_backup)