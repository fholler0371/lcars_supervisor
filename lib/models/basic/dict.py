from pydantic import BaseModel, Field

class Dict(BaseModel):
    data : dict = Field(default={}) 