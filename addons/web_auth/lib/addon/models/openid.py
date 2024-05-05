from pydantic import BaseModel, Field


class OpenId(BaseModel):
    sub : str = Field(alias= 'user_id_s')
    iss : str
    iat : int 
    exp : int 
    aud : str
    name : str|None = None
    role : str|None = None
    email : str|None = None