from models.msg.msg_base import MsgBase, MSG_DIRECT

from .app_reg import NotifyApp

class MsgNotifyRegApp(MsgBase):
    type : int = MSG_DIRECT
    path : str = 'register_notify_app'
    data : dict
