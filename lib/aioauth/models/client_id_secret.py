import pydantic


class ClientIdSecret(pydantic.BaseModel):
    clientid: str
    secret: str