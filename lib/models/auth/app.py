from pydantic import BaseModel, Field
import time

def timestamp():
    return int(time.time())
               
class App(BaseModel):
    app: str
    url: str
    icon: str
    label: str
    time: int = Field(default_factory=timestamp)
