import secrets
import pathlib

import aioyamllib

import time
class LocalKeys:
    def __init__(self, core: any) -> None:
        self.core = core
        
    async def _ainit(self, sv: bool= False):
        if sv:
            self.file = pathlib.Path('/'.join(str(self.core.path.data).split('/')[:-1])) / 'supervisor' / 'local_keys.yml'
        else:
            self.file = self.core.path.data / 'local_keys.yml'
        if self.file.exists():
            self.data = await aioyamllib.save_load(self.file)
        else:
            self.data = {'local': secrets.token_hex(32)}
            await self._save()
            self.core.log.info('lokalen Key erstellt')
            
    async def _save(self):
        await aioyamllib.dump(self.file, self.data)
        
    def __getattr__(self, name):
        return self.data.get(name, None)
