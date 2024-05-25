from pydantic import BaseModel


class UserMail(BaseModel):
    mail : str
