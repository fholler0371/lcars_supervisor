import secrets
import pathlib
import os

import aioyamllib

import time
class LocalKeys:
    def __init__(self, core: any) -> None:
        self.__core = core
        self.__data = None
        self.__file = None
        
    async def _ainit(self, sv: bool= False):
        if sv:
            self.__file = pathlib.Path('/'.join(str(self.__core.path.data).split('/')[:-1])) / 'supervisor' / 'local_keys.yml'
        else:
            self.__file = self.__core.path.data / 'local_keys.yml'
        if self.__file.exists():
            self.__data = await aioyamllib.save_load(self.__file)
        elif self.__core.const.is_docker:
            self.__data = {'local': os.getenv('LCARS_KEY')}
        else:
            self.__data = {'local': secrets.token_hex(32)}
            await self.__save()
            self.__core.log.info('lokalen Key erstellt')
            
    async def __save(self):
        await aioyamllib.dump(self.__file, self.__data)
        
    def __getattr__(self, name):
        if name == 'keys':
            return self.__data.keys()
        return self.__data.get(name, None)
