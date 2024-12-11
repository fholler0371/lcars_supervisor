from aiohttp import web
import json
import time

from corelib import BaseObj, Core

from httplib.models import HttpHandler, HttpRequestData, SendOk
from models.network import Hostname
from models.basic import StringList, StringEntry

from models.msg import MsgGetLocalApps  

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def get_apps_from_docker(self):
        apps = []
        for container in await self.core.docker.containers.list():
            if 'pro.holler.lcars.python' in container.labels:
                apps.append(container.name)
        return apps
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        msg_type = 0
        try:
            msg_type = json.loads(rd.data).get('type', 0)
        except:
            ...
        if msg_type == 1 and rd.auth:
            match '/'.join(rd.path):
                case 'network/get_local_apps':
                    return (True, web.json_response(SendOk(data=StringList(data=await self.get_apps_from_docker())).model_dump()))
        else:
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
                    try:
                        for host in self.core._local_keys.keys:
                            hostname = host if host != 'local' else await self.core.web_l.hostname
                            app_data = self._apps.setdefault(hostname, {'valid': 0, 'apps': []}) 
                            if app_data['valid'] < time.time():
                                if host == 'local':
                                    apps = await self.get_apps_from_docker()
                                    self._apps[hostname] = app_data = {'valid': time.time()+self.core.random(600),
                                                                'apps': apps}
                                else:
                                    apps = []
                                    try:
                                        if resp := await self.core.lc_req.msg(host=host, app='gateway', msg=MsgGetLocalApps()):
                                            try:
                                                apps = resp['data']['data']
                                            except:
                                                ...
                                    except Exception as e:
                                        self.core.log.error(repr(e)) 
                                    self._apps[hostname] = app_data = {'valid': time.time()+self.core.random(600),
                                                                        'apps': apps}
                            hostname = host if host != 'local' else await self.core.web_l.hostname
                            print(hostname)
                            print(app_data)
                            try:
                                _out.data.extend([f'{hostname}.{name}' for name in app_data['apps']])
                            except:
                                ...
                    except Exception as e:
                        self.core.log.error(repr(e))    
                    print(_out)
                    return (True, web.json_response(_out.model_dump()))
                case 'messages/get_ip6':
                    resp = await self.core.web_l.get('network/ip6', dest='parent')
                    out = StringList(data=resp.get('ip6_addr'))
                    return (True, web.json_response(out.model_dump()))    
                case 'messages/get_docker_gateway_by_container':
                    _data = rd.data.data
                    self.core.log.critical(_data)
                    resp = await self.core.web_l.post('network/container_gateway', dest='parent', data=_data)
                    out = StringEntry(data=resp.get('gateway'))
                    return (True, web.json_response(out.model_dump()))    
                case _:
                    self.core.log.debug(rd)
        return False
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')
        await self.core.web.add_handler(HttpHandler(domain = 'com', func = self.handler, auth='local', acl='lcars'))

    async def _astart(self):
        self.core.log.debug('starte com')
