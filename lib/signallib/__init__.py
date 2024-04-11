import asyncio
import signal
from corelib import BaseObj, Core

from pprint import pprint


class Signal(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def _ainit(self):
        for signame in ('SIGINT', 'SIGTERM', 'SIGHUP'):
            self.core.const.loop.add_signal_handler(getattr(signal, signame),
                            lambda signame=signame: asyncio.create_task(self.got_signal(signame)))
            
    async def got_signal(self, signame):
        self.core.log.info(f'Signal erhalten {signame}')
        if signame == 'SIGHUP':
            self.core.const.reload = True
        self.core.running.set()
