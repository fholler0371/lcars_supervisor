import pydantic


class SendOk(pydantic.BaseModel):
    ok : bool = True