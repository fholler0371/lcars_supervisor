from pydantic import BaseModel, Field

class StringList(BaseModel):
    data : list[str] = Field(default=[]) 