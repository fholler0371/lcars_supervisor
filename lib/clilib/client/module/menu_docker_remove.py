import aiofiles.os as os
import aiotomllib
import aioyamllib
from functools import partial
import pathlib

import clilib.data as cd

import time


class MenuDockerRemove:
    def __init__(self, core):
        self.core = core
        self.step = 'main/docker/doc_remove'
        self.menu_entries = []
        self.table = None
    
    async def update_data(self):
        self.menu_entries.clear()
        resp = await self.core.web_l.get('docker/running')
        if resp is None:
            return
        resp = [cd.CliContainer(**x) for x in resp]
        for entry in resp:
            self.menu_entries.append({'label': entry.label, 'action': partial(self.add_addons, name= entry.name)})
    
    async def add_addons(self, name: str) -> None:
        await self.core.web_l.post('docker/deactivate', {'addon': name})
