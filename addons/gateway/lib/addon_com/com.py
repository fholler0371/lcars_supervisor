from aiohttp import web
import time 

from corelib import BaseObj, Core

from httplib.models import HttpHandler, HttpRequestData
from models.network import Hostname
from models.basic import StringList

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'network/hostname':
                if self.core.web_l._hostname:
                    return (True, web.json_response({'hostname': self.core.web_l._hostname}))
                resp = await self.core.web_l.get('network/hostname', dest='parent')
                if resp is not None:
                    self.core.web_l._hostname = resp.get('hostname')
                if self.core.web_l._hostname:
                    return (True, web.json_response(Hostname(hostname=self.core.web_l._hostname).model_dump()))
            case 'network/app_list':
                _out = StringList()
                for host in self.core.web_l.local_keys.data.keys():
                    app_data = self._apps.setdefault(host, {'valid': 0, 'apps': []}) 
                    if app_data['valid'] < time.time():
                        if host == 'local':
                            apps = []
                            for container in await self.core.docker.containers.list():
                                if 'pro.holler.lcars.python' in container.labels:
                                    apps.append(container.name)
                        self._apps[host] = app_data = {'valid': time.time()+self.core.random(600),
                                                       'apps': apps}
                    if host == 'local':
                        hostname = await self.core.web_l.hostname
                    _out.data.extend([f'{hostname}.{name}' for name in app_data['apps']])
                return (True, web.json_response(_out.model_dump()))
            case _:
                self.core.log.debug(rd)
        return False
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='docker'))

    async def _astart(self):
        self.core.log.debug('starte com')
