from pydantic import BaseModel


class IpData(BaseModel):
    ip4: str|None = None
    prefix: str|None = None