from pydantic import BaseModel, Field


class TokenByCode(BaseModel):
    clientid: str|None = Field(alias='client_id', default=None)
    secret: str = Field(alias='client_secret')
    callback: str = Field(alias='redirect_uri', default=None)
    code: str 
    grant_type: str
