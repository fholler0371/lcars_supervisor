import threading
import asyncio


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
