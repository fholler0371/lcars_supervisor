import pydantic


class RedirectUrl(pydantic.BaseModel):
    redirect_url : str = pydantic.Field(alias='url')
