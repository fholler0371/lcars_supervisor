import asyncio
import importlib

import aiopathlib
import constlib
import configlib
import loggerlib
import signallib

from .core import Core
from .helper import Secret, LocalKeys, LcarsRequests

class DockerCore(Core):
    def __init__(self) -> None:
        Core.__init__(self)
        
    async def run_it(self):
        await self.add('path', aiopathlib.Path)
        await self.add('const', constlib.Const)
        await self.add('cfg', configlib.Config, toml=self.path.config / 'config.toml',
                                                acl=self.path.config / 'acl.toml',
                                                manifest=self.path.config / 'manifest.toml')
        # laden der Bibliotheken vor dem Start von Logger um die internen Logger zu Kontrollieren
        classes_pre = {}
        if self.cfg.manifest is not None:
            for key, cl_name in self.cfg.manifest.get('libs', {}).get('load_pre', {}).items():
                mod_name, cl_name = cl_name.split('.', 1)
                mod = importlib.import_module(mod_name)
                classes_pre[key] = getattr(mod, cl_name)
        classes = {}
        if self.cfg.manifest is not None:
            for key, cl_name in self.cfg.manifest.get('lib', {}).items():
                mod_name, cl_name = cl_name.split('.', 1)
                mod = importlib.import_module(mod_name)
                classes[key] = getattr(mod, cl_name)
        await self.add('log', loggerlib.Logger)
        await self.add('running', asyncio.Event())
        await self.add('signal', signallib.Signal)
        await self.add('secret', Secret)
        await self.add('_local_keys', LocalKeys)
        await self.add('lc_req', LcarsRequests)
        for key, cls in classes_pre.items():
            await self.add(key, cls)
        for key, cls in classes.items():
            await self.add(key, cls)
        self.log.info(f'starte {self.const.app} (pid: {self.const.pid})')
        await self.start()
        await self.running.wait()
        await self.stop()
        self.log.info(f'stoppe {self.const.app}')
