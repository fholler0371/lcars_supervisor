import pydantic
from typing import Any


class HttpHandler(pydantic.BaseModel):
    domain : str
    acl : str = 'lcars'
    func : Any = None
    remote : str = None
    auth : bool|str = False
    auth_exeption : Any = None
