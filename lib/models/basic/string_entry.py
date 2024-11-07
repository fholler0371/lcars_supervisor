from pydantic import BaseModel, Field

class StringEntry(BaseModel):
    data : str|None = None 