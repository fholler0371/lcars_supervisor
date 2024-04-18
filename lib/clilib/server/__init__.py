from aiohttp import web
import aiofiles.os as os
from datetime import datetime as dt
from datetime import UTC

from corelib import BaseObj, Core

import aiotomllib
import aioyamllib


class Server(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def _ainit(self):
        await self.core.web.add_handler('/cli/', self.pre_handler)
        
    async def pre_handler(self, request: web.Request) -> bool:
        data = {'version': 0, 'auth': False, 'path': ''}
        try:
            data['version'] = int(request.path.split('/')[2])
        except:
            self.core.log.error('Keine gültige Version im Pfad')
        if 'X-Auth' in request.headers:
            header = request.headers['X-Auth']
            if header == self.core.web.local_keys.local:
                data['auth'] = True
            else:
                self.core.log.error('Ungülter Auth Key')
                return (True, web.Response(status=403, text='Nicht erlaubt'))
        else:
            self.core.log.error('Kein Autorisation Handler')
            return (True, web.Response(status=403, text='Nicht erlaubt'))
        data['path'] = '/'.join(str(request.path).split('/')[3:])
        try:
            data['json'] = await request.json()
        except:
            data['json'] = {}
        return await self.handler(request, data)

    async def handler(self, request: web.Request, data: dict) -> bool:
        match data['path']:
            case 'docker/avaible':
                return await self.cli_docker_avaible()
            case 'docker/activate':
                return await self.cli_docker_activate(data['json'])
            case 'docker/running':
                return await self.cli_docker_running()
            case 'docker/deactivate':
                return await self.cli_docker_deactivate(data['json'])
            case 'docker/status':
                return await self.cli_docker_status()
        return False
    
    async def cli_docker_avaible(self) -> None:
        data = {}
        for entry in await os.scandir(str(self.core.path.base / 'addons')):
            cfg_file = self.core.path.base / 'addons' / entry.name / 'manifest.toml'
            cfg = await aiotomllib.loader(cfg_file)
            data[cfg['name']] = cfg['label']
        for container in await self.core.docker.containers.list():
            if container.name in data:
                del data[container.name]
        return (True, web.json_response(data))

    async def cli_docker_activate(self, data: dict) -> None:
        file = self.core.path.data / "docker.yml"
        cfg = await aioyamllib.save_load(file)
        if cfg is None:
            cfg = {'apps':[]}
        if data['addon'] not in cfg['apps']:
            cfg['apps'].append(data['addon'])
        await aioyamllib.dump(file, cfg)
        return (True, web.json_response({}))

    async def cli_docker_running(self) -> tuple:
        data = {}
        containers = await self.core.docker.containers.list()
        for container in containers:
            if 'pro.holler.lcars.managed' in container.labels:
                cfg_file = self.core.path.base / 'addons' / container.name / 'manifest.toml'
                cfg = await aiotomllib.loader(cfg_file)
                if cfg is None:
                    continue
                data[cfg['name']] = cfg['label']
        return (True, web.json_response(data))

    async def cli_docker_deactivate(self, data: dict) -> None:
        file = self.core.path.data / "docker.yml"
        cfg = await aioyamllib.save_load(file)
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
                rec = {'name': container.name, 'lcars': False}
            else:
                cfg_file = self.core.path.base / 'addons' / container.name / 'manifest.toml'
                cfg = await aiotomllib.loader(cfg_file)
                if cfg is None:
                    continue
                rec = {'name': cfg['label'], 'lcars': True}
            rec['status'] = container.status
            if (state := container.attrs['State'].get('Health', {}).get('Status')) is not None:
                rec['status'] = state
            rec['network'] = ''
            rec['ip'] = ''
            if 'Networks' in container.attrs['NetworkSettings']:
                for label, netdata in container.attrs['NetworkSettings']['Networks'].items():
                    rec['network'] = label
                    if 'IPAddress' in netdata:
                        rec['ip'] = netdata['IPAddress']
            epoch = dt.strptime('1970-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S')
            rec['start'] = int((dt.strptime(container.attrs['State']['StartedAt'][:19], '%Y-%m-%dT%H:%M:%S') - epoch).total_seconds())
            rec['created'] = int((dt.strptime(container.attrs['Created'][:19], '%Y-%m-%dT%H:%M:%S') - epoch).total_seconds())
            data.append(rec)
        data = sorted(data, key=lambda x: x['name'])
        return (True, web.json_response(data))
