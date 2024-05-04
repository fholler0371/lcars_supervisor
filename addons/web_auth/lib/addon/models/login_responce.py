from pydantic import BaseModel


class LoginResponce(BaseModel):
    login_token : str
    redirect_url : str