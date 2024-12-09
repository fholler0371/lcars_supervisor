from models.msg import MsgBase



class LcarsRequests:
    def __init__(self, core: object) -> None:
        self.__core = core
    
    async def msg(self, app: str, msg: MsgBase, host: str|None = None) -> dict:
        self.__core.log.info(app)
        self.__core.log.info(msg)
        self.__core.log.info(host)