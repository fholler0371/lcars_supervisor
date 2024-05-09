from pydantic import BaseModel, Field
from typing import Any


class HttpRequestData(BaseModel):
    path : list[str]
    acl_check : bool = False
    version : int = 0
    auth : bool = False
    data : Any = Field(default=[])
    ip : str = None
    host : str = None
    scheme : str = None
    open_id : dict|None = None
    domain: str = ''
