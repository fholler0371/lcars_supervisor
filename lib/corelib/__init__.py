Core = object

class BaseObj:
    def __init__(self, core: Core) -> None:
        self.core = Core

class Core:
    async def add(self, name: str, obj: object, *args, **kwargs) -> None:
        try:
            setattr(self, name, _obj := obj(self, *args, **kwargs))
            if hasattr(_obj, '_ainit'):
                await _obj._ainit()
        except:
            setattr(self, name, obj)
