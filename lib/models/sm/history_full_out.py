from pydantic import BaseModel, Field


class HistoryFullOut(BaseModel):
    label: str
    decimal: int = 2
    data : list[dict] = Field(default=[])
    factor : float = 1
