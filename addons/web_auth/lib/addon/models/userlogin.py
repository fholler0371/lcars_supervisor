import pydantic


class UserLogin(pydantic.BaseModel):
    response_type: str|None = None
    callback: str|None = pydantic.Field(alias='redirect_uri', default=None)
    clientid: str|None = pydantic.Field(alias='client_id', default=None)
    scope: str|None = None
    state: str|None = None
    name: str|None = None
    password: str|None = None
    totp: str|None = None
    ip: str|None = None
    
    secure: bool = False
    
    app_id: int = -1
    app_name: str = ''
    
    user_id: int = -1
    user_id_s: str = ''
    roles: str = ''
    
    @property
    def valid(self):
        return self.app_id > 0 and self.user_id > 0