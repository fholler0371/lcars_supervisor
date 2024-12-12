from models.msg.msg_base import MsgBase, MSG_DIRECT


class MsgAppList(MsgBase):
    type : int = MSG_DIRECT
    path : str = 'network/app_list'
