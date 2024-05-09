from pydantic import BaseModel, Field
import time


class App(BaseModel):
    app: str
    url: str
    icon: str
    label: str
    time: int = Field(default=int(time.time()))
