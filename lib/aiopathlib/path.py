import pathlib
import threading

from corelib import BaseObj, Core

from .helper import th_cmd

        
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