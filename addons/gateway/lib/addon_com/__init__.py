from aiohttp import web
import time

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.data import HttpHandler, HttpRequestData


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
                    return (True, web.json_response({'hostname': self.core.web_l._hostname}))
            case 'network/app_list':
                out = []
                for host in self.core.web_l.local_keys.data.keys():
                    app_data = self._apps.setdefault(host, {'valid': 0, 'apps': []}) 
                    if app_data['valid'] < time.time():
                        if host == 'local':
                            resp = await self.core.web_l.get('docker/status', dest='parent')
                            resp = [cd.CliStatus(**x) for x in resp]
                        try:
                            self._apps[host] = app_data = {'valid': time.time()+self.core.random(600),
                                                       'apps': [d.docker_name for d in resp if d.python]}
                        except Exception as e:
                            print(e, flush=True)
                    if host == 'local':
                        hostname = await self.core.web_l.hostname
                    out.extend([f'{hostname}.{name}' for name in app_data['apps']])
                return (True, web.json_response(out))
        return False
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='docker'))
        pass
        #await self.core.web.add_handler(HttpHandler(domain = 'cli', func = self.handler, auth='local'))

    async def _astart(self):
        self.core.log.debug('starte com')
