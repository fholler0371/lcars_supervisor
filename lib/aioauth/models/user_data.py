import pydantic


class UserData(pydantic.BaseModel):
    name: str
    password: str