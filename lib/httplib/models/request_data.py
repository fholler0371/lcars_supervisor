import pydantic
from typing import Any


class HttpRequestData(pydantic.BaseModel):
    path : list[str]
    acl_check : bool = False
    version : int = 0
    auth : bool = False
    data : Any = None
