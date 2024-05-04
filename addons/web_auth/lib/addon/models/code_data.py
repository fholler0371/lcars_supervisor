import pydantic


class CodeData(pydantic.BaseModel):
    clientid: str
    scope: str|None = None
    state: str|None = None
    secure: bool = False
    app_id: int = -1
    app_name: str = ''
    user_id: int = -1
    user_id_s: str = ''
    roles: str = ''
