import asyncio

from fritzconnection import FritzConnection

class Avm_Connection:
    def __init__(self, core, ip, user, password):
        self.core = core
        #self._ip = None
        #self._user = None
        #self._password = None
        self._fc = None
        self._FritzStatus = None
        self._version = None
        try:
            self._fc = FritzConnection(address=ip, user=user, password=password, use_cache=True)
            self._version = repr(self._fc).split('\n')[1]
        except Exception as e:
            self.core.log.error(e)

    async def version(self):
        if self._version:
            return self._version
        
    async def call_action(self, modul, action):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._fc.call_action, modul, action)
        
    async def get_ipv4(self):
        try:
            return (await self.call_action("WANIPConn", "GetExternalIPAddress"))['NewExternalIPAddress']
        except Exception as e:
            self.core.log.error(e)
            return 'error'

    async def get_ipv6(self):
        try:
            return (await self.call_action("WANIPConn", "X_AVM_DE_GetExternalIPv6Address"))['NewExternalIPv6Address']
        except Exception as e:
            self.core.log.error(e)
            return 'error'

    async def get_ipv6_prefix(self):
        try:
            data = await self.call_action("WANIPConn", "X_AVM_DE_GetIPv6Prefix")
            return data['NewIPv6Prefix'] + '/' + str(data['NewPrefixLength'])
        except Exception as e:
            self.core.log.error(e)
            return 'error'
