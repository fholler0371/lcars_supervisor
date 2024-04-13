import docker

from corelib import BaseObj

from .networks import Networks
from .container import Container


class Docker(BaseObj):
    def __init__(self, core: any, sock: str = "/var/run/docker.sock") -> None:
        BaseObj.__init__(self, core)
        self.sock = f'unix:/{sock}'
        self.client = None
        
    async def _ainit(self) -> any:
        self.client = await self.core.const.loop.run_in_executor(None, docker.DockerClient, self.sock)
        self.networks = Networks(self.core, self.client)        
        self.containers = Container(self.core, self.client)