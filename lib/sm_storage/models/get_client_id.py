import pydantic


class GetClientId(pydantic.BaseModel):
    app: str
    callback: str