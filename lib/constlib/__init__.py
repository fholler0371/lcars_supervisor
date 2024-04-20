import socket
import asyncio
import os
import sys
import aiofiles
import aiofiles.os

from corelib import BaseObj, Core


PIDFILE = '/run/lcars-supervisor.pid'
class Const(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        try:
            self.hostname = socket.getfqdn()
        except:
            self.core.log.warning('hostname nicht gefunden')
            self.hostname = ''
        self.pid = os.getpid()
        self.reload = False
        self.app = sys.argv[0].split('/')[-1].split('.')[0]
        self.is_docker = os.getenv('LCARS_CONTAINER', default='0') == str(1)
        
    async def _ainit(self):
        self.loop = asyncio.get_event_loop()
        if self.app == "supervisord":
            try:
                async with aiofiles.open(PIDFILE, 'w') as f:
                    await f.write(str(self.pid))
            except Exception as e:
                print(e)

    async def _astop(self):
        if self.app == "supervisord":
            await aiofiles.os.remove(PIDFILE)
