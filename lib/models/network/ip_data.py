from pydantic import BaseModel


class IpData(BaseModel):
    ip4: str