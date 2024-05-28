from corelib import BaseObj, Core

class Cache(BaseObj):
    def __init__(self, core: Core, sv: bool= False) -> None:
        BaseObj.__init__(self, core)
                
    async def _ainit(self):
        self.core.log.debug('Initaliesiere cache')

    async def _astart(self):
        self.core.log.debug('starte cache')

    async def _astop(self):
        self.core.log.debug('stoppe cache')
