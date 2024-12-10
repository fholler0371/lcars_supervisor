from pydantic import BaseModel

MSG_NONE : int = 0
MSG_DIRECT : int = 1

class MsgBase(BaseModel):
    type : int = MSG_NONE
    path : str = 'network/get_local_apps'
    data : dict|None = None