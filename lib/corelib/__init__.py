Core = object

class BaseObj:
    def __init__(self, core: Core) -> None:
        self.core = core

class Core:
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
