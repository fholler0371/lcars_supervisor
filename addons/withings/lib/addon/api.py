import tomllib
import time

from corelib import BaseObj, Core


class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
                
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
                   
    async def _astart(self):
        self.core.log.debug('starte api')

    async def _astop(self):
        self.core.log.debug('stoppe api')
