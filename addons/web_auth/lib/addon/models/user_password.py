from pydantic import BaseModel


class UserPassword(BaseModel):
    password : str
    password_new : str
    password_repeat : str
    
    @property
    def valid(self) -> bool:
        if self.password_new != self.password_repeat:
            return False
        if len(self.password_new) < 8:
            return False
        return True
