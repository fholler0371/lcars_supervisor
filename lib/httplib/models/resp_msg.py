import pydantic
from typing import Any


class RespRaw(pydantic.BaseModel):
    headers : dict 
    content : Any