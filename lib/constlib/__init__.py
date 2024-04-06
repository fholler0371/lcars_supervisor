import socket
import asyncio

from corelib import BaseObj, Core


class Const(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        try:
            self.hostname = socket.getfqdn()
        except:
            self.hostname = ''
        self.is_docker = False
        
    async def _ainit(self):
        self.loop = asyncio.get_event_loop()
        
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