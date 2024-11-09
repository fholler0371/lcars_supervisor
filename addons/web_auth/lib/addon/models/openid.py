from pydantic import BaseModel, Field


class OpenId(BaseModel):
    sub : str = Field(alias= 'user_id_s')
    iss : str
    iat : int 
    exp : int 
    aud : str
    loc : int|None = 0
    name : str|None = None
    role : str|None = None
    app : str|None = None
    email : str|None = None