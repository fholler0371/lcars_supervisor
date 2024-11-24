from corelib import BaseObj, Core
import time

from httplib.models import HttpMsgData

from .models import CacheEntry


class WebCache(BaseObj):
    def __init__(self, core: Core, sv: bool= False) -> None:
        BaseObj.__init__(self, core)
        self._sensors = {}
        
    async def get_value(self, sensor):
        if sensor in self._sensors and self._sensors[sensor].valid:
            return self._sensors[sensor].value
        else:
            _app, _sensor = sensor.split('.', 1)
            if resp := await self.core.web_l.msg_send(HttpMsgData(dest=_app, 
                                                                  type='sm/get_sensor', 
                                                                  data={'sensor': _sensor})):
                self._sensors[sensor] = CacheEntry.model_validate(resp['data'])
                return self._sensors[sensor].value
            return None

    async def get_history(self, sensor, interval):
        self.core.log.debug(f"get history: {sensor} {interval}")
        _app, _sensor = sensor.split('.', 1)
        if resp := await self.core.web_l.msg_send(HttpMsgData(dest=_app, 
                                                              type='sm/get_history', 
                                                              data={'sensor': _sensor, 'interval': interval})):
            return resp['data'] if resp['ok'] else None
        return None

                
    async def _ainit(self):
        self.core.log.debug('Initaliesiere cache')

    async def _astart(self):
        self.core.log.debug('starte cache')

    async def _astop(self):
        self.core.log.debug('stoppe cache')
