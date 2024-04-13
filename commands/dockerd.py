import sys
if __name__ == "__main__":
    sys.path.append(sys.argv[1]+'/lib')
import asyncio
import pathlib
import aiofiles
import aiofiles.os as os

import corelib
import constlib
import sv_pathlib
import configlib
import aiodockerlib
import aioyamllib
import aiotomllib


from pprint import pprint


async def check_network(core: corelib.Core, name: str, data: any) -> None:
    if (net := await core.docker.networks.get(name)) is not None:
        return
    match data["type"]:
        case 'bridge':
            p = await asyncio.subprocess.create_subprocess_shell(
                f'docker network create --attachable --ip-range {data["subnet"]} --subnet {data["subnet"]} --gateway={data["gateway"]} ' +
                f'--opt com.docker.network.bridge.name={data["adapter"]} ' + 
                f'--opt com.docker.network.container_iface_prefix={data["interface"]} {name}', 
                stderr=asyncio.subprocess.PIPE, 
                stdout=asyncio.subprocess.PIPE)
            _, stderr = await p.communicate()
            if stderr.decode() != '':
                p = await asyncio.subprocess.create_subprocess_shell(
                    'sudo systemctl restart docker', 
                    stderr=asyncio.subprocess.PIPE, 
                    stdout=asyncio.subprocess.PIPE)
                await p.wait()
            else:
                core.running.set()

async def main() -> None:
    core = corelib.Core()
    await core.add('const', constlib.Const)
    await core.add('path', sv_pathlib.Path, pathlib.Path(sys.argv[2]) / 'data' / 'supervisor' / 'folder.yml')
    await core.add('cfg', configlib.Config, toml=core.path.config / core.const.hostname / 'config.toml')
    await core.add('running', asyncio.Event())
    await core.add('docker', aiodockerlib.Docker)
    for name, data in core.cfg.toml.get('networks', {}).items():
        if core.running.is_set():
            break
        await check_network(core, name, data)
    container_data = await aioyamllib.save_load(core.path.data / 'docker.yml')
    if not (core.path.temp / 'compose').exists():
        await os.mkdir(core.path.temp / 'compose', force=True)
    for container in container_data.get('apps', []):
        if await core.docker.containers.get(container) is None:
            toml = await aiotomllib.loader(core.path.base / 'addons' / container / 'docker_data.toml')
            comp = {}
            comp['services'] = {}
            comp['services'][toml['name']] = {}
            comp['services'][toml['name']]['image'] = toml['image']
            comp['services'][toml['name']]['container_name'] = toml['name']
            if 'ports' in toml:
                comp['services'][toml['name']]['ports'] = []
                for port in toml['ports']:
                    comp['services'][toml['name']]['ports'].append(port)
            if 'networks' in toml:
                comp['networks'] = {}
                idx = 1
                comp['services'][toml['name']]['networks'] = []
                for network in toml['networks']:
                    comp['networks'][f'net{idx}'] = {'external': True, 'name': network}
                    comp['services'][toml['name']]['networks'].append(f'net{idx}')
                    idx += 1
            if 'volumes' in toml:
                comp['services'][toml['name']]['volumes'] = []
                data_folder = pathlib.Path('/'.join(str(core.path.data).split('/')[:-1])) / toml['name'] 
                for source, dest in toml['volumes'].items():
                    source = source.replace('%data_folder%', str(data_folder))
                    comp['services'][toml['name']]['volumes'].append(f"{source}:{dest}")
            if 'restart' in toml:
                comp['services'][toml['name']]['restart'] = toml['restart']
            comp['services'][toml['name']]['labels'] = ["pro.holler.lcars.managed=true"]
            await aioyamllib.dump(core.path.temp / 'compose/portainer.yml', comp)    
            cmd = f"docker compose -f {str(core.path.temp / 'compose/portainer.yml')} up -d"    
            p = await asyncio.subprocess.create_subprocess_shell(
                cmd, 
                stderr=asyncio.subprocess.PIPE, 
                stdout=asyncio.subprocess.PIPE)
            await p.wait()
            if p.returncode != 0:
                p = await asyncio.subprocess.create_subprocess_shell(
                    'systemctl restart docker', 
                    stderr=asyncio.subprocess.PIPE, 
                    stdout=asyncio.subprocess.PIPE)
                await p.wait()
                p = await asyncio.subprocess.create_subprocess_shell(
                    cmd, 
                    stderr=asyncio.subprocess.PIPE, 
                    stdout=asyncio.subprocess.PIPE)
                await p.wait()
            return

    
    #print(sys.path)
    #print(sys.argv)
    #print('dockerd')

if __name__ == "__main__":
    asyncio.run(main())
