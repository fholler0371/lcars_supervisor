from pydantic import BaseModel, Field


class Moduls(BaseModel):
    ok : bool = True
    moduls : list[dict] = Field(default=[])
    
    def append(self, data: dict) -> None:
        self.moduls.append(data)
    