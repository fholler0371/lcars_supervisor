import pydantic
from typing import Any

class SendOk(pydantic.BaseModel):
    ok : bool = True
    data : Any|None = None