from aiohttp import web
from netaddr import IPAddress, IPNetwork

from .webserver import server_start
from .local_keys import LocalKeys
from .client_local import ClientLocal
from .data import HttpHandler, HttpRequestData, HttpMsgData

from corelib import BaseObj, Core



class HTTP(BaseObj):
    def __init__(self, core: Core, sv: bool= False) -> None:
        BaseObj.__init__(self, core)
        self._sv = sv
        self._handlers = []
        self.acl_lcars = ['127.0.0.1/32']
        self.acl_lcars_docker = ['127.0.0.1/32']
        self.acl_home = ['127.0.0.1/32']
        self.acl_docker = []
        if self.core.cfg.acl is not None and (ip := self.core.cfg.acl.get('lcars')) is not None:
            self.acl_lcars.append(ip)
            self.acl_lcars_docker.append(ip)
            self.acl_home.append(ip)
        if self.core.cfg.acl is not None and (ip := self.core.cfg.acl.get('docker')) is not None:
            self.acl_docker.append(ip)
            self.acl_lcars_docker.append(ip)
            self.acl_home.append(ip)
        if self.core.cfg.acl is not None and (ip := self.core.cfg.acl.get('home')) is not None:
            self.acl_home.append(ip)
        
    async def add_handler(self, h : HttpHandler) -> None:
        self.core.log.debug(f'Registrier Handler für: {h.domain}')
        idx_found = -1
        for idx, item in enumerate(self._handlers):
            if item.domain == h.domain:
                self._handlers[idx] = h
                break
        else:
            self._handlers.append(h)
        
    async def _handler(self, request: web.Request):
        self.core.log.debug(f'{request.remote} {request.method} {request.path}')
        rd = HttpRequestData(path=request.path.split('/'))
        for entry in self._handlers:
            if entry.domain == rd.path[1]:
                rd.path = rd.path[2:]
                rd.acl_check = self.acl_check(request.remote, entry.acl)
                if not rd.acl_check:
                    self.core.log.error(f'acl sagt nicht erlaubt')
                    return web.Response(status=403)
                try:
                    if len(rd.path) and (version := int(rd.path[0])):
                        rd.version = version
                        rd.path = rd.path[1:]
                except:
                    pass #keine Version
                if entry.auth:
                    match entry.auth:
                        case 'local':
                            if 'X-Auth' in request.headers:
                                rd.auth = request.headers['X-Auth'] == self.core.web.local_keys.local
                    if not rd.auth:
                        self.core.log.error(f'Authentication nicht gültig')
                        return web.Response(status=403)
                if request.method == 'POST':
                    try:
                        rd.data = await request.json()
                    except Exception as e:
                        #print(e)
                        pass
                if request.method == 'GET':
                    try:
                        rd.data = dict(request.rel_url.query)
                    except Exception as e:
                        pass
                if entry.func is not None:
                    if resp := await entry.func(request, rd):
                        return resp[1]
                if entry.remote is not None:
                    data = HttpMsgData(dest= entry.remote, type= f'messages/relay', 
                                       data= rd.model_dump_json())
                    resp = await self.core.web_l.msg_send(data)
                    self.core.log.debug(resp)
        else:
            return web.Response(text="OK")
        
    def acl_check(self, ip: str, acl: str) -> bool:
        allowed = False
        match acl:
            case 'lcars':
                ranges = self.acl_lcars
            case 'docker':
                ranges = self.acl_docker
            case 'lcars_docker':
                ranges = self.acl_lcars_docker
            case 'home':
                ranges = self.acl_home
        try:
            _ip = IPAddress(ip)
            for acl_ip in ranges:
                if _ip in IPNetwork(acl_ip):
                    return True
        except Exception as e:
            self.core.log.error(e)
        return False
        

    async def _ainit(self):
        self.core.log.debug('starte WebServer')
        try:
            port = 1234 if self._sv else 1235
            self.site = await server_start(port, self._handler)
            self.local_keys = LocalKeys(self.core)
            await self.local_keys._ainit()
            self.core.log.info(f'WebServer hört auf Port {port}')
        except Exception as e:
            self.core.running.set()
            self.core.log.error(e)
    
    async def _astop(self):
        self.core.log.info('WebServer gestopt')