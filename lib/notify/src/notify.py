from corelib import BaseObj, Core

from ..models import NotifyApp, NotifyMessage, MsgNotifyRegApp


class Notify(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self.__notify_token = None
        
    async def _astart(self):
        self.core.log.debug('starte notify')
        await self.core.call_random(20, self._register_notify)

    async def _register_notify(self)->None:
        self.core.log.debug('get_notify_token')
        if self.__notify_token is None:
            await self.core.call_random(60, self._register_notify)
            data = NotifyApp(label= self.core.cfg.manifest['app_data']['label_short'],
                             icon= self.core.cfg.manifest['app_data']['icon'],
                             app= self.core.cfg.manifest['name'])
            try:
                resp = await self.core.lc_req.msg(app='web_notify', msg=MsgNotifyRegApp(data=data))
            except Exception as e:
                print(e)
            self.core.log.critical(data)
            
            if resp and resp['ok']:
                self.__notify_token = resp['data']['data']
            self.core.log.debug(f"NotifyToken: {self.__notify_token}")
