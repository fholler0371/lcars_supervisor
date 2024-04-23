import aiopathlib

from .core import Core

class DockerCore(Core):
    def __init__(self) -> None:
        Core.__init__(self)
        
    async def run_it(self):
        await self.add('path', aiopathlib.Path)
