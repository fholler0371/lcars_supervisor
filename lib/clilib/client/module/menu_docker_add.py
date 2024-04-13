import aiofiles.os as os
import aiotomllib
import aioyamllib
from functools import partial
import pathlib


class MenuDockerAdd:
    def __init__(self, core):
        self.core = core
        self.step = 'main/doc_add'
        self.menu_entries = []
        
    async def update_data(self):
        data = {}
        for entry in await os.scandir(str(self.core.path.base / 'addons')):
            cfg_file = self.core.path.base / 'addons' / entry.name / 'manifest.toml'
            cfg = await aiotomllib.loader(cfg_file)
            data[cfg['name']] = cfg['label']
        for container in await self.core.docker.containers.list():
            if container.name in data:
                del data[container.name]
        self.menu_entries.clear()
        for entry, label in data.items():
            self.menu_entries.append({'label': label, 'action': partial(self.add_addons, name= entry)})
            print(entry, label)
    
    async def add_addons(self, name: str) -> None:
        file = pathlib.Path(str(self.core.path.data).replace(self.core.const.app, 'supervisor')) / "docker.yml"
        cfg = await aioyamllib.save_load(file)
        if cfg is None:
            cfg = {'apps':[]}
        if name not in cfg['apps']:
            cfg['apps'].append(name)
        await aioyamllib.dump(file, cfg)
    