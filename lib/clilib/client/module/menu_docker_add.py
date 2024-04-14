import aiofiles.os as os
import aiotomllib
import aioyamllib
from functools import partial
import pathlib

import time


class MenuDockerAdd:
    def __init__(self, core):
        self.core = core
        self.step = 'main/doc_add'
        self.menu_entries = []
        
    async def update_data(self):
        self.menu_entries.clear()
        resp = await self.core.web_l.get('docker/avaible')
        if resp is None:
            return
        for entry, label in resp.items():
            self.menu_entries.append({'label': label, 'action': partial(self.add_addons, name= entry)})
    
    async def add_addons(self, name: str) -> None:
        await self.core.web_l.post('docker/activate', {'addon': name})
        return
        print(name)
        file = pathlib.Path(str(self.core.path.data).replace(self.core.const.app, 'supervisor')) / "docker.yml"
        cfg = await aioyamllib.save_load(file)
        if cfg is None:
            cfg = {'apps':[]}
        if name not in cfg['apps']:
            cfg['apps'].append(name)
        await aioyamllib.dump(file, cfg)
    