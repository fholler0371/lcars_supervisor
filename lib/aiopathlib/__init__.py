import pathlib
import asyncio
import threading

from corelib import BaseObj, Core


class th_cmd(threading.Thread):
    def __init__(self, ev: threading.Event,  cmd: str) -> None:
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.ev = ev
    
    async def run_cmd(self)->None:
        p = await asyncio.subprocess.create_subprocess_shell(self.cmd, 
                                                            stderr=asyncio.subprocess.PIPE, 
                                                            stdout=asyncio.subprocess.PIPE)
        await p.wait() 
        self.ev.set()
        pass
    
    def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.run_cmd())
        
class Path(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self.cfg = None
        
    async def _ainit(self) -> any:
        self.cfg = {'base': '/lcars',
                    'lcars': '/lcars',
                    'data': '/lcars/data'}
        
    def __getattr__(self, propName: str) -> any:
        if propName.startswith('_'):
            raise AttributeError
        try:
            if path := self.cfg.get(propName, None):
                return pathlib.Path(path)
            self.cfg[propName] = str(self.cfg.get('data')).replace('data', propName)
            cmd = f'mkdir -p {str(self.cfg[propName])}'
            ev = threading.Event()
            th = th_cmd(ev, cmd)
            th.start()
            ev.wait(10)
            return pathlib.Path(self.cfg[propName])

        except Exception as e:
            return self.cfg.get(propName)