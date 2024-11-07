from aiohttp import web
import aiofiles.os as os
from datetime import datetime as dt
from datetime import UTC
import socket
import json
import tomllib
import psutil as ps

from ..data import CliStatus, CliContainer
from httplib.models import HttpHandler, HttpRequestData

from corelib import BaseObj, Core


import aiotomllib
import aioyamllib


class Server(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def _ainit(self):
        await self.core.web.add_handler(HttpHandler(domain = 'cli', func = self.handler, auth='local', acl='lcars_docker'))
        
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        match '/'.join(rd.path):
            case 'docker/avaible':
                return await self.cli_docker_avaible()
            case 'docker/activate':
                return await self.cli_docker_activate(rd.data)
            case 'docker/running':
                return await self.cli_docker_running()
            case 'docker/deactivate':
                return await self.cli_docker_deactivate(rd.data)
            case 'docker/status':
                return await self.cli_docker_status()
            case 'network/hostname':
                return (True, web.json_response({'hostname': socket.getfqdn()}))
            case 'network/ip6':
                data = []
                for rec in ps.net_if_addrs().get(self.core.cfg.toml['network']['ip6_interface'], []):
                    if rec.family == 10:
                        data.append(rec.address)
                return (True, web.json_response({'ip6_addr': data}))
        return False
    
    async def cli_docker_avaible(self) -> None:
        data = []
        containers = await self.core.docker.containers.list()
        for entry in await os.scandir(str(self.core.path.base / 'addons')):
            cfg_file = self.core.path.base / 'addons' / entry.name / 'manifest.toml'
            cfg = await aiotomllib.loader(cfg_file)
            for container in containers:
                if container.name in cfg['name']:
                    break
            else: 
                data.append(CliContainer(name=cfg['name'], label=cfg['label']))
        return (True, web.json_response([d.model_dump() for d in sorted(data, key=lambda x: x.label)]))

    async def cli_docker_activate(self, data: dict) -> None:
        file = self.core.path.data / "docker.yml"
        try:
            cfg = await aioyamllib.save_load(file)
            if isinstance(data, str):
                data = json.loads(data)
            if cfg is None:
                cfg = {'apps':[]}
            if data['addon'] not in cfg['apps']:
                cfg['apps'].append(data['addon'])
            await aioyamllib.dump(file, cfg)
        except Exception as e:
            self.core.log.error(e)
        return (True, web.json_response({}))

    async def cli_docker_running(self) -> tuple:
        data = []
        containers = await self.core.docker.containers.list()
        for container in containers:
            if 'pro.holler.lcars.managed' in container.labels:
                cfg_file = self.core.path.base / 'addons' / container.name / 'manifest.toml'
                cfg = await aiotomllib.loader(cfg_file)
                if cfg is None:
                    continue
                data.append(CliContainer(name=cfg['name'], label=cfg['label']))
        return (True, web.json_response([d.model_dump() for d in sorted(data, key=lambda x: x.label)]))

    async def cli_docker_deactivate(self, data: dict) -> None:
        file = self.core.path.data / "docker.yml"
        cfg = await aioyamllib.save_load(file)
        if isinstance(data, str):
            data = json.loads(data)
        if cfg is None:
            cfg = {'apps':[]}
        if data['addon'] in cfg['apps']:
            cfg['apps'].remove(data['addon'])
        await aioyamllib.dump(file, cfg)
        return (True, web.json_response({}))

    async def cli_docker_status(self) -> tuple:
        data = []
        containers = await self.core.docker.containers.list()
        for container in containers:
            if 'pro.holler.lcars.managed' not in container.labels:
                d_rec = CliStatus(name=container.name, docker_name=container.name)
            else:
                cfg_file = self.core.path.base / 'addons' / container.name / 'manifest.toml'
                cfg = await aiotomllib.loader(cfg_file)
                if cfg is None:
                    continue
                d_rec = CliStatus(name=cfg['label'], docker_name=cfg['name'], lcars=True)
            if 'pro.holler.lcars.python' in container.labels:
                d_rec.python = True
            d_rec.status = container.status
            if d_rec.status == 'running' and (state := container.attrs['State'].get('Health', {}).get('Status')) is not None:
                d_rec.status = state
            if 'Networks' in container.attrs['NetworkSettings']:
                for label, netdata in container.attrs['NetworkSettings']['Networks'].items():
                    d_rec.network = label
                    if 'IPAddress' in netdata:
                        d_rec.ip = netdata['IPAddress']
            epoch = dt.strptime('1970-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S')
            d_rec.start = int((dt.strptime(container.attrs['State']['StartedAt'][:19], '%Y-%m-%dT%H:%M:%S') - epoch).total_seconds())
            d_rec.created = int((dt.strptime(container.attrs['Created'][:19], '%Y-%m-%dT%H:%M:%S') - epoch).total_seconds())
            data.append(d_rec)
        return (True, web.json_response([d.model_dump() for d in sorted(data, key=lambda x: x.name)]))
