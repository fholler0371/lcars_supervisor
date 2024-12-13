from asyncio import Lock
from aiohttp import web
import json
import time

from corelib import BaseObj, Core

from httplib.models import HttpHandler, HttpRequestData, SendOk
from models.network import Hostname
from models.basic import StringList, StringEntry

from models.msg import MsgGetLocalApps, MsgRelay, MsgBase, MSG_DIRECT, MSG_RELAY

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        self.__hostname = None
        self.__lock_local_apps = Lock()
        self.__lock_app_list = Lock()
        
    async def get_apps_from_docker(self):
        apps = []
        for container in await self.core.docker.containers.list():
            if 'pro.holler.lcars.python' in container.labels:
                apps.append(container.name)
        return apps
        
    async def get_app_list(self):
        try:
            _out = StringList()
            for host in self.core._local_keys.keys:
                hostname = host if host != 'local' else await self.core.web_l.hostname
                app_data = self._apps.setdefault(hostname, {'valid': 0, 'apps': []}) 
                if app_data['valid'] < time.time():
                    if host == 'local':
                        apps = await self.get_apps_from_docker()
                        self._apps[hostname] = app_data = {'valid': time.time()+self.core.random(600), 'apps': apps}
                    else:
                        apps = []
                        if resp := await self.core.lc_req.msg(host=host, app='gateway', msg=MsgGetLocalApps(), host_check=False):
                            try:
                                apps = resp['data']
                            except Exception as e:
                                self.core.log.error(f"{host} {resp}")
                                self.core.log.error(repr(e))
                        self._apps[hostname] = app_data = {'valid': time.time()+self.core.random(600), 'apps': apps}
                _out.data.extend([f'{hostname}.{name}' for name in app_data['apps']])
            #self.core.log.critical(_out)
            return _out
        except Exception as e:
            self.core.log.error(repr(e))
                        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        msg_type = 0
        try:
            msg_type = json.loads(rd.data).get('type', 0)
        except:
            ...
        if msg_type == MSG_DIRECT and rd.auth:
            self.core.log.info(f"call(type 1) {'/'.join(rd.path)}") 
            match '/'.join(rd.path):
                case 'network/get_local_apps':
                    try:
                        async with self.__lock_local_apps:
                            return (True, web.json_response(StringList(data=await self.get_apps_from_docker()).model_dump()))
                    except Exception as e:
                        self.core.log.error(repr(e))
                case 'network/app_list':
                    async with self.__lock_app_list:
                        out = await self.get_app_list()
                    return (True, web.json_response(out.model_dump()))
                case 'network/hostname':
                    try:
                        print('network/hostname')
#                        if self.__hostname:
                        return (True, web.json_response({'hostname': await self.core.web_l.hostname}))
                        # TODO:  CONVERT Parent Communication
                        resp = await self.core.web_l.get('network/hostname', dest='parent')
                        if resp is not None:
                            self.__hostname = resp.get('hostname')
                        if self.__hostname:
                            return (True, web.json_response(Hostname(hostname=self.__hostname).model_dump()))
                    except Exception as e:
                        self.core.log.error(repr(e))
            return False
        elif msg_type == MSG_RELAY and rd.auth:
            self.core.log.info(f"call(type 2) {'/'.join(rd.path)}") 
            match '/'.join(rd.path):
                case 'relay':
                    data = json.loads(rd.data)
                    host = data.get('dest_host')
                    del data['dest_host']
                    app = data.get('dest_app')
                    del data['dest_app']
                    path = data.get('dest_path')
                    del data['type']
                    if host == await self.core.web_l.hostname:
                        self.core.log.critical(data)
                        del data['dest_path']
                        msg = MsgBase(data=data, type=MSG_DIRECT, path=path)
                        if resp := await self.core.lc_req.msg(app=app, msg=msg, host_check=False):
                            self.core.log.critical(resp)
                            return (True, web.json_response(resp))
                    else:
                        msg = MsgRelay(host=host, app=app, data=data)
                        if resp := await self.core.lc_req.msg(host=host, app='gateway', msg=msg, host_check=False):
                            return (True, web.json_response(resp))
        else:
            match '/'.join(rd.path):
                case 'network/hostname':
                    if not self.core.web_l._hostname:
                        resp = await self.core.web_l.get('network/hostname', dest='parent')
                        if resp is not None:
                            self.core.web_l._hostname = resp.get('hostname')
                    print(self.core.web_l._hostname)
                    if self.core.web_l._hostname:
                        return (True, web.json_response(Hostname(hostname=self.core.web_l._hostname).model_dump()))
                case 'network/app_list':
                    print('yyy')
                    async with self.__lock_app_list:
                        out = await self.get_app_list()
                    return (True, web.json_response(out.model_dump()))
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
