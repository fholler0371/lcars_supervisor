import pydantic


class UserLogin(pydantic.BaseModel):
    response_type: str|None = None
    callback: str|None = pydantic.Field(alias='redirect_uri', default=None)
    scope: str|None = None
    state: str|None = None
    name: str|None = None
    password: str|None = None
    totp: str|None = None
    ip: str|None = None
    secure: bool = False