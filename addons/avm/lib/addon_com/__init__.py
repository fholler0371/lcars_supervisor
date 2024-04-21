from corelib import BaseObj, Core


class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        pass
        #await self.core.web.add_handler(HttpHandler(domain = 'cli', func = self.handler, auth='local'))

    async def _astart(self):
        try:
            h = await self.core.web_l.hostname
            print(h, flush=True)
        except Exception as e:
            print(e, flush=True)
        self.core.log.debug('starte com')
