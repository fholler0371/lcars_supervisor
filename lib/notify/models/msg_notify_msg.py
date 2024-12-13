from models.msg.msg_base import MsgBase, MSG_DIRECT

from .messages import NotifyMessage

class MsgNotifyMsg(MsgBase):
    type : int = MSG_DIRECT
    path : str = 'notify_message'
    data : NotifyMessage
