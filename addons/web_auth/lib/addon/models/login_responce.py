from pydantic import BaseModel


class LoginResponce(BaseModel):
    ok : bool = True
    login_token : str
    redirect_url : str