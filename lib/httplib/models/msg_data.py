import pydantic
from typing import Any


class HttpMsgData(pydantic.BaseModel):
    dest: str
    type: str
    data: Any|None = None