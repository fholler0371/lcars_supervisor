from typing import Any
from pathlib import Path

from corelib import BaseObj, Core
import aiotomllib


class Config(BaseObj):
    def __init__(self, core: Core, toml: Path = None, acl: Path = None, manifest: Path = None) -> None:
        BaseObj.__init__(self, core)
        self._toml_name = toml
        self.toml = None
        self._acl_name = acl
        self.acl = None
        self._manifest_name = manifest
        self.manifest = None
        
    async def _ainit(self) -> None:
        if self._toml_name is not None:
            self.toml = await aiotomllib.loader(self._toml_name)
            if self.core.const.is_docker:
                self.core.const.app = self.toml.get('app', self.core.const.app)
        if self._acl_name is not None:
            self.acl = await aiotomllib.loader(self._acl_name)
        if self._manifest_name is not None:
            self.manifest = await aiotomllib.loader(self._manifest_name)

    def __getattr__(self, name: str) -> Any:
        value = self.toml.get(name)
        if value:
            return value
