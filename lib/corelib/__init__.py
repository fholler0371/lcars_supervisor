from typing import Any
from functools import partial
import time


Core = object

class BaseObj:
    def __init__(self, core: Core) -> None:
        self.core = core
        
class LogDummy:
    LEVEL = {'critical', 'error', 'warning', 'info', 'debug'}
    
    def _log(self, msg: str, level:str ) -> None:
        print(f'{level.upper()} {msg}')

    def __getattr__(self, name: str) -> Any:
        if name in self.LEVEL:
            return partial(self._log, level=name)

class Core:
    def __init__(self) -> None:
        self.log = LogDummy()    
    
    async def add(self, name: str, obj: object, *args, **kwargs) -> None:
        try:
            setattr(self, name, _obj := obj(self, *args, **kwargs))
            if hasattr(_obj, '_ainit'):
                await _obj._ainit()
            return
        except Exception as e:
            #print(name, repr(e))
            pass
        setattr(self, name, obj)
