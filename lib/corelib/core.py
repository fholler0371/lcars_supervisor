from functools import partial
from typing import Any
import random




Core = object

class BaseObj:
    def __init__(self, core: Core) -> None:
        self.core = core

class LogDummy:
    LEVEL = {'critical', 'error', 'warning', 'info', 'debug'}
    
    def _log(self, msg: str, level:str ) -> None:
        print(f'{level.upper()} {msg}', flush=True)

    def __getattr__(self, name: str) -> Any:
        if name in self.LEVEL:
            return partial(self._log, level=name)

class Core:
    def __init__(self) -> None:
        self.log = LogDummy()    
        
    async def start(self):
        for entry in self.__dir__():
            if entry.startswith('__'):
                continue
            if not hasattr((obj := getattr(self, entry)), 'core'):
                continue
            if hasattr(obj, '_astart'):
                if (func := getattr(obj, '_astart')) is not None:
                    await self.call(func)
    
    async def stop(self):
        for entry in self.__dir__():
            if entry.startswith('__'):
                continue
            if not hasattr((obj := getattr(self, entry)), 'core'):
                continue
            if hasattr(obj, '_astop'):
                if (func := getattr(obj, '_astop')) is not None:
                    await func()

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
        
    def random(self, delay: int) -> int:
        return random.random() * 0.2 * delay + 0.9 * delay
        
    async def call_random(self, random_delay, callback, *args, **kwargs):
        await self.call_delay(self.random(random_delay), callback, *args, **kwargs)
        
    async def call_delay(self, delay, callback, *args, **kwargs):
        self.const.loop.call_later(delay, self._run, callback, *args, **kwargs)
    
    async def call(self, callback, *args, **kwargs):
        self.const.loop.call_soon(self._run, callback, *args, **kwargs)

    def _run(self, callback, *args, **kwargs):
        self.const.loop.create_task(callback(*args, **kwargs))