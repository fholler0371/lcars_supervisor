from pydantic import BaseModel, Field


class Moduls(BaseModel):
    ok : bool = True
    moduls : list[dict] = Field(default=[])