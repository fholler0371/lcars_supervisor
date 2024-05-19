from pydantic import BaseModel


class UserLabel(BaseModel):
    label : str
