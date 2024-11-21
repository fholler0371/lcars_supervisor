from pydantic import BaseModel, Field

class Device(BaseModel):
    id : str = Field(alias="deviceid")
    type : str
    model : str
    battery : str
    