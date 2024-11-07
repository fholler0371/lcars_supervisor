from aiohttp import web
import pathlib
import aioyamllib
import netaddr

from corelib import BaseObj, Core
from httplib.models import HttpMsgData, HttpHandler, HttpRequestData, SendOk

from .models import AvmDynDns, IpState
from models.network import IpData
from models.basic import StringEntry, StringList

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._state = IpState()
        self._home = StringEntry(data='_home')
        self._state_name = pathlib.Path('/lcars/data/ip_state.yml')
        
    async def save(self, repeat: bool = True) -> None:
        if repeat:
            await self.core.call_random(1800, self.save)
        try:
            if self._state.changed:
                self.core.log.debug('speichere aktuellen Status in Datei')
                await aioyamllib.dump(self._state_name, self._state.model_dump())
                self._state.changed = False
        except Exception:
            self.core.log.error(Exception)

    async def on_update(self) -> None:
        if self._state.change or self._state.home_ip6:
            resp = await self.core.web_l.msg_send(HttpMsgData(dest='gateway', type='get_ip6'))
            try:
                data = StringList(data=resp.get('data', []))
                net = netaddr.IPNetwork(self._state.prefix)
                for entry in data.data:
                    try:
                        ip = netaddr.IPAddress(entry)
                        if ip in net:
                            self._state.home_ip6 = entry
                            self._state.change = False
                    except Exception as e:
                        self.core.log.error(repr(e))
            except Exception as e:
                self.core.log.error(repr(e))
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        if rd.path[0] == 'messages':
            msg = HttpMsgData.model_validate(rd.data)
            match rd.path[1]:
                case 'relay':
                    relay_rd = HttpRequestData.model_validate(msg.data)
                    if relay_rd.path[0] == 'dyndns':
                        dyndns_data = AvmDynDns.model_validate(relay_rd.data)
                        for key, value in dyndns_data.model_dump().items():
                            if value != '':
                                if hasattr(self._state, key):
                                    self._state.update(**{key: value})
                        self.core.log.debug(dyndns_data)
                        await self.core.call(self.on_update)
                        return (True, web.json_response(SendOk().model_dump()))
                case 'get_ip':
                    data = IpData(ip4=self._state.ip4)
                    return (True, web.json_response(data.model_dump()))
                case 'get_all_ip':
                    #self.core.log.critical(self._state)
                    data = IpData(ip4=self._state.ip4, prefix=self._state.prefix, ip6=self._state.ip6, home_ip6=self._state.home_ip6)
                    #self.core.log.critical(data)
                    return (True, web.json_response(data.model_dump()))
                        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='lcars_docker'))
        if self._state_name.exists():
            try:
                self._state = IpState(**(await aioyamllib.save_load(self._state_name)))
                self._state.changed = False
            except Exception as e:
                self.core.log.error(e)

    async def register_web_app(self)->None:
        self.core.log.debug('do register')
        await self.core.call_random(300, self.register_web_app)
        data = HttpHandler(domain='avm', acl='home', 
                           remote=f'{await self.core.web_l.hostname}.{self.core.const.app}')
        try:
            await self.core.web_l.msg_send(HttpMsgData(dest='web_base', type='register_web_app', data=data))
        except Exception as e:
           self.core.log.error(e)
           
    async def _astart(self):
        self.core.log.debug('starte com')
        await self.core.call_random(10, self.register_web_app)
        await self.core.call_random(1800, self.save)

    async def _astop(self):
        self.core.log.debug('stoppe com')
        await self.save(repeat=False)
