import asyncio
from aiohttp import web
import aiohttp
from netaddr import IPAddress, IPNetwork
import urllib.parse
import time

from corelib import BaseObj, Core
import cryptlib

from .models import HttpMsgData, HttpHandler, HttpRequestData, RespRaw
from .webserver import server_start
from .local_keys import LocalKeys


class HTTP(BaseObj):
    def __init__(self, core: Core, sv: bool= False) -> None:
        BaseObj.__init__(self, core)
        self._sv = sv
        self._jwt = None
        self._handlers = []
        self._static_handler = None
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
        
    async def add_handler(self, h : HttpHandler, static: bool = False) -> None:
        if static:
            self._static_handler = h
            return
        self.core.log.debug(f'Registrier Handler für: {h.domain}')
        idx_found = -1
        for idx, item in enumerate(self._handlers):
            if item.domain == h.domain:
                self._handlers[idx] = h
                break
        else:
            self._handlers.append(h)
        
    async def _handler(self, request: web.Request):
        try:
            rd = HttpRequestData(path=request.path.split('/'),
                                 ip=x if (x := request.headers.get('X-Real-IP')) else request.remote,
                                 host=x if (x := request.headers.get('X-Host')) else request.host,
                                 scheme=x if (x := request.headers.get('X-Forwarded-Scheme')) else request.scheme)
            self.core.log.debug(f'{rd.ip} {request.method} {request.path}')
            self.core.log.debug(request.headers)
        except Exception as e:
            self.core.log.error(e)
        for entry in self._handlers:
            if entry.domain == rd.path[1]:
                rd.path = rd.path[2:]
                rd.domain = entry.domain
                rd.acl_check = self.acl_check(rd.ip, entry.acl)
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
                        try: 
                            rd.data = HttpMsgData.model_validate(rd.data)
                        except Exception as e:
                            try:
                                rd.data = await request.text()
                            except:
                                pass
                    except Exception as e:
                        rd.data = await request.text()
                        #print(e)
                        pass
                    if isinstance(rd.data, str):
                        try:
                            data = {}
                            for values in urllib.parse.parse_qsl(rd.data):
                                data[values[0]] = values[1]
                            if data:
                                rd.data = data
                        except:
                            pass
                if request.method == 'GET':
                    try:
                        rd.data = dict(request.rel_url.query)
                    except Exception as e:
                        pass
                if 'Authorization' in request.headers:
                    try:
                        token = request.headers.get('Authorization').split(' ')[-1]
                        if self._jwt is None:
                            url = f'{rd.scheme}://{rd.host}/auth/pem'
                            pem = await self.core.web_l.get_raw(url)
                            if pem is not None:
                                self._jwt = cryptlib.Jwt(pem)
                        if self._jwt:
                            rd.open_id = self._jwt.validate(token)
                            if rd.open_id['exp'] < time.time():
                                rd.open_id = None
                    except Exception as e:
                        self.core.log.error(e)
                if entry.func is not None:
                    try:
                        if resp := await entry.func(request, rd):
                            #print('118', resp, flush=True)
                            return resp[1]
                    except Exception as e:
                        self.core.log.error(e)
                if entry.remote is not None:
                    data = HttpMsgData(dest= entry.remote, type= f'relay', 
                                       data= rd.model_dump())
                    resp = await self.core.web_l.msg_send(data)
                    if isinstance(resp, RespRaw):
                        return web.Response(body=resp.content, headers=resp.headers, status=resp.status)
                    return resp[1]
        else:
            if self._static_handler is not None:
                if resp := await self._static_handler.func(request, rd):
                    return resp[1]
            self.core.log.critical("not handled")
            self.core.log.critical(request.path)
            return web.Response(text="OK")
        
    def acl_check(self, ip: str, acl: str) -> bool:
        if acl is None:
            return True
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