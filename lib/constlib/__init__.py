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
        self.is_docker = False
        
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

        
'''
import os, re

path = "/proc/self/cgroup"

def is_docker():
  if not os.path.isfile(path): return False
  with open(path) as f:
    for line in f:
      if re.match("\d+:[\w=]+:/docker(-[ce]e)?/\w+", line):
        return True
    return False

print(is_docker())
'''