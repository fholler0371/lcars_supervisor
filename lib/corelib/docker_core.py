import asyncio

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
                                                acl=self.path.config / 'acl.toml')
        await self.add('log', loggerlib.Logger)
        await self.add('running', asyncio.Event())
        await self.add('signal', signallib.Signal)
