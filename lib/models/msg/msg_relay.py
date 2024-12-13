from models.msg.msg_base import MsgBase, MSG_RELAY


class MsgRelay(MsgBase):
    type : int = MSG_RELAY
    path : str = 'relay'
    app: str
    host: str
    app_path: str
