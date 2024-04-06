from pathlib import Path

from corelib import BaseObj, Core
import aiotomllib


class Config(BaseObj):
    def __init__(self, core: Core, toml: Path = None) -> None:
        BaseObj.__init__(self, core)
        self._toml_name = toml
        self.toml = None
        
    async def _ainit(self) -> None:
        if self._toml_name is not None:
            self.toml = await aiotomllib.loader(self._toml_name)
