import aioyamllib
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
        
class th_save(threading.Thread):
    def __init__(self, file: str,  data: dict) -> None:
        threading.Thread.__init__(self)
        self.file = file
        self.data = data
    
    async def run_save(self)->None:
        await aioyamllib.dump(self.file, self.data)
    
    def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.run_save())
class Path(BaseObj):
    def __init__(self, core: Core, file: str) -> None:
        BaseObj.__init__(self, core)
        self.file = file
        
    async def _ainit(self) -> any:
        self.cfg = await aioyamllib.save_load(self.file)
        self.cfg = {} if self.cfg is None else self.cfg  

    def __getattr__(self, propName: str) -> any:
        try:
            if path := self.cfg.get(propName, None):
                return pathlib.Path(path)
            self.cfg[propName] = str(self.cfg.get('data')).replace('data', propName)
            cmd = f'mkdir -p {str(self.cfg[propName])}'
            ev = threading.Event()
            th = th_cmd(ev, cmd)
            th.start()
            ev.wait(10)
            th_save(self.file, self.cfg).start()
            return pathlib.Path(self.cfg[propName])

        except Exception as e:
            return self.cfg.get(propName)