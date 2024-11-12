from pydantic import BaseModel, Field

class ListOfDict(BaseModel):
    data : list[dict] = Field(default=[]) 