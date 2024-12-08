import secrets
from pathlib import Path
import os

import aioyamllib


class LocalKeys:
    def __init__(self, core: any) -> None:
        self.__core : object = core
        self.__data : dict = None
        self.__file : dict = None
        self.__ip : dict = None
        
    async def _ainit(self, sv: bool= False) -> None:
        if sv:
            self.__file = Path('/'.join(str(self.__core.path.data).split('/')[:-1])) / 'supervisor'
        else:
            self.__file = self.__core.path.data 
        self.__file /= 'local_keys.yml'
        if self.__file.exists():
            self.__data = await aioyamllib.save_load(self.__file)
        elif self.__core.const.is_docker:
            self.__data = {'local': os.getenv('LCARS_KEY')}
            #add keys von secrets
            if secret_data := self.__core.secret.lcars:
                self.__core.log.info(secret_data)
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
