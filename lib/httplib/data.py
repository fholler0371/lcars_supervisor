import pydantic
from typing import Any


class HttpHandler(pydantic.BaseModel):
    domain : str
    acl : str = 'lcars'
    func : Any = None
    remote : str = None
    auth : bool|str = False
    auth_exeption : Any = None
    
class HttpRequestData(pydantic.BaseModel):
    path : list[str]
    acl_check : bool = False
    version : int = 0
    auth : bool = False
    data : Any = None

class HttpMsgData(pydantic.BaseModel):
    dest: str
    type: str
    data: Any