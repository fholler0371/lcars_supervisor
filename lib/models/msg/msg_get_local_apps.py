from models.msg.msg_base import MsgBase, MSG_DIRECT


class MsgGetLocalApps(MsgBase):
    type : int = MSG_DIRECT
    path : str = 'network/get_local_apps'
