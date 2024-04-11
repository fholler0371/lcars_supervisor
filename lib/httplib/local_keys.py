import secrets

import aioyamllib


class LocalKeys:
    def __init__(self, core: any) -> None:
        self.core = core
        
    async def _ainit(self):
        self.file = self.core.path.data / 'local_keys.yml'
        if self.file.exists():
            self.data = aioyamllib.save_load(self.file)
        else:
            self.data = {'local': secrets.token_hex(32)}
            await self._save()
            self.core.log.info('lokalen Key erstellt')
            
    async def _save(self):
        await aioyamllib.dump(self.file, self.data)
        
    def __getattr__(self, name):
        return self.data.get('name', None)
