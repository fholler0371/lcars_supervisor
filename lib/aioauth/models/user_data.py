import pydantic


class UserData(pydantic.BaseModel):
    name: str
    password: str
    roles: str    
    roles_secure: str
    apps: str    
    apps_secure: str