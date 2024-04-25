import asyncio
import importlib

import aiopathlib
import constlib
import configlib
import loggerlib
import signallib

from .core import Core

class DockerCore(Core):
    def __init__(self) -> None:
        Core.__init__(self)
        
    async def run_it(self):
        await self.add('path', aiopathlib.Path)
        await self.add('const', constlib.Const)
        await self.add('cfg', configlib.Config, toml=self.path.config / 'config.toml',
                                                acl=self.path.config / 'acl.toml',
                                                manifest=self.path.config / 'manifest.toml')
        await self.add('log', loggerlib.Logger)
        await self.add('running', asyncio.Event())
        await self.add('signal', signallib.Signal)
        if self.cfg.manifest is not None:
            for key, cl_name in self.cfg.manifest.get('lib', {}).items():
                mod_name, cl_name = cl_name.split('.', 1)
                mod = importlib.import_module(mod_name)
                cls = getattr(mod, cl_name)
                await self.add(key, cls)
