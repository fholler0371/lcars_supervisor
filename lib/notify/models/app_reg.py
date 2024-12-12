from pydantic import BaseModel
               
class NotifyApp(BaseModel):
    app: str
    icon: str
    label: str
