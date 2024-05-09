from pydantic import BaseModel, Field


class Apps(BaseModel):
    ok : bool = True
    moduls : list[dict] = Field(default=[])
    
    def append(self, data: dict) -> None:
        self.moduls.append(data)
    
    def sort(self):
        pass