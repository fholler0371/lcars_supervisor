from pydantic import BaseModel, Field

#{'hostname': 'holler.pro', 'ipv4': '92.116.229.65', 'ipv6': '2001:9e8:34:8fc9:e228:6dff:feed:312f', 'prefix': '2001:9e8:186d:7400::/64'}
class AvmDynDns(BaseModel):
    hostname : str
    ip4 : str = Field(alias='ipv4')
    ip6 : str = Field(alias='ipv6')
    prefix : str