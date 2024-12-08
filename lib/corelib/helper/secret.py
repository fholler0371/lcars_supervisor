import aiotomllib as toml
from pathlib import Path


class Secret:
    def __init__(self, core: object) -> None:
        self.__core : object = core
        self.__data : dict = {}
        
    async def _ainit(self) -> None:
        self.__core.log.info('init secret')
        self.__allowed = self.__core.cfg.manifest.get('secret', [])
        file_name : Path = self.__core.path.config / 'secret.toml'
        data : dict|None = None
        try:
            if file_name.exists():
                data = await toml.loader(file_name)
        except Exception as e:
            self.__core.log.error(repr(e))
        if data is None:
            data = {} 
        for key in data.keys():
            if key in self.__allowed:
                self.__data[key] = data[key]
        self.__core.log.info(self.__data)

    def __getattr__(self, name:str) -> dict|None:
        return self.__data.get(name)