import tomllib
import time

from corelib import BaseObj, Core

import addon

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._ac = None
                
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        with open("/lcars/config/secret.toml", "rb") as f:
            secret = tomllib.load(f)
        secret_avm = secret['avm']
        try:
            self._ac = addon.Avm_Connection(self.core, secret_avm['ip'], secret_avm['user'], secret_avm['pass'])
        except Exception as e:
            self.core.log.error(e)
        self.core.log.debug(await self._ac.version())
        
    async def check_ip_info(self):
        await self.core.call_random(300, self.check_ip_info)
        self.core.com._state.update(**{'ip4': await self._ac.get_ipv4()})
        self.core.com._state.update(**{'ip6': await self._ac.get_ipv6()})
        self.core.com._state.update(**{'prefix': await self._ac.get_ipv6_prefix()})
        await self.core.call(self.core.com.on_update)
           
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.check_ip_info)
        return
        await self.core.call_random(10, self.register_web_app)
        await self.core.call_random(1800, self.save)

    async def _astop(self):
        self.core.log.debug('stoppe api')
        return
        await self.save(repeat=False)
