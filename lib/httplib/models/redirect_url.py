import pydantic


class RedirectUrl(pydantic.BaseModel):
    ok : bool = True
    redirect_url : str = pydantic.Field(alias='url')
