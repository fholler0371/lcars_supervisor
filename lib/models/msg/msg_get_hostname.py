from models.msg.msg_base import MsgBase, MSG_DIRECT


class MsgGetHostName(MsgBase):
    type : int = MSG_DIRECT
    path : str = 'network/hostname'
