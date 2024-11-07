from pydantic import BaseModel


class IpData(BaseModel):
    ip4: str|None = None
    ip6: str|None = None
    prefix: str|None = None    
    home_ip6: str|None = None