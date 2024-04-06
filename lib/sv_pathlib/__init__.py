import aioyamllib
import pathlib

from corelib import BaseObj, Core


class Path(BaseObj):
    def __init__(self, core: Core, file: str) -> None:
        BaseObj.__init__(self, core)
        self.file = file
        
    async def _ainit(self) -> any:
        self.cfg = await aioyamllib.save_load(self.file)
        self.cfg = {} if self.cfg is None else self.cfg  

    def __getattr__(self, propName: str) -> any:
        try:
            if path := self.cfg.get(propName):
                return pathlib.Path(path)
            return path
        except:
            return self.cfg.get(propName)