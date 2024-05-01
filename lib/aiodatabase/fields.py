class Field:
    def __init__(self, name, **kwargs) -> None:
        self._name = name
        self._type = None
        self._default = kwargs.get('default', None)

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

class Integer(Field):
    def __init__(self, name, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self._type = "INTEGER"
        self._autoincrement = kwargs.get('autoincrement', False)

class Text(Field):
    def __init__(self, name, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self._type = "TEXT"
