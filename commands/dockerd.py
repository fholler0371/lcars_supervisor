import sys
if __name__ == "__main__":
    sys.path.append(sys.argv[1]+'/lib')
import asyncio
import pathlib
import aiofiles
import aiofiles.os as os
from functools import partial
from datetime import datetime as dt

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
                
async def create_image(core: corelib.Core, image_name: str, image_folder: str) -> None:
    docker_file = core.path.base / 'images' / image_folder / 'Dockerfile'
    p = await asyncio.subprocess.create_subprocess_shell(
            'lsb_release -a', 
            stderr=asyncio.subprocess.PIPE, 
            stdout=asyncio.subprocess.PIPE)
    out, err = await p.communicate()
    codename = ""
    for line in out.decode().split('\n'):
        if line.startswith('Codename'):
            codename = line.split('\t')[-1]
    lines = ''
    async with aiofiles.open(docker_file) as f:
        lines = await f.read()
    lines = lines.replace('%codename%', codename)
    docker_file = core.path.temp / f"{image_folder}.Dockerfile"
    async with aiofiles.open(docker_file, 'w') as f:
        await f.write(lines)
    cfg_toml_file = core.path.base / 'images' / image_folder / "config.toml"
    if cfg_toml_file.exists():
        cfg_toml = await aiotomllib.loader(cfg_toml_file)
        for file_name in cfg_toml.get('copy', []):
            cmd = f"cp {core.path.base / 'images' / image_folder / file_name} { core.path.temp / file_name}"
            p = await asyncio.subprocess.create_subprocess_shell(
                cmd, 
                stderr=asyncio.subprocess.PIPE, 
                stdout=asyncio.subprocess.PIPE)
            await p.wait()
    cmd = f"docker build {core.path.temp} -t lcars/python:2024.04 -f {docker_file}"
    p = await asyncio.subprocess.create_subprocess_shell(
        cmd, 
        stderr=asyncio.subprocess.PIPE, 
        stdout=asyncio.subprocess.PIPE)
    await p.wait()
                
async def container_add(core: corelib.Core, container: str) -> None:
    #check image 
    manifest = await aiotomllib.loader(core.path.base / 'addons' / container / 'manifest.toml')
    if (img_name := manifest.get('docker', {}).get('name')):
        if '%Y' in img_name:
            d = dt.now()
            img_name = d.strftime(img_name)
        to_build = True
        for image in await core.docker.images.list():
            for tag in image.attrs['RepoTags']:
                if tag == img_name:
                    to_build = False
                    break
            if not to_build:
                break
        if to_build:
            await create_image(core, img_name, manifest.get('docker', {}).get('folder'))
    toml = await aiotomllib.loader(core.path.base / 'addons' / container / 'docker_data.toml')
    comp = {}
    comp['services'] = {}
    comp['services'][toml['name']] = {}
    img_name = toml['image'] 
    if '%Y' in img_name:
        d = dt.now()
        img_name = d.strftime(img_name)
    comp['services'][toml['name']]['image'] = img_name
    comp['services'][toml['name']]['container_name'] = toml['name']
    if 'ports' in toml:
        comp['services'][toml['name']]['ports'] = []
        for port in toml['ports']:
            comp['services'][toml['name']]['ports'].append(port)
    if 'environment' in toml:
        comp['services'][toml['name']]['environment'] = []
        for environment in toml['environment']:
            comp['services'][toml['name']]['environment'].append(environment)
    if toml.get('setup', {}).get('lcars'):
        if 'environment' not in comp['services'][toml['name']]:
            comp['services'][toml['name']]['environment'] = []
        keys = await aioyamllib.save_load(pathlib.Path(sys.argv[2]) / 'data' / 'supervisor' / 'local_keys.yml')
        comp['services'][toml['name']]['environment'].append(f"LCARS_KEY={keys.get('local', '')}")
    if 'networks' in toml:
        comp['networks'] = {}
        idx = 1
        comp['services'][toml['name']]['networks'] = []
        for network in toml['networks']:
            comp['networks'][f'net{idx}'] = {'external': True, 'name': network}
            comp['services'][toml['name']]['networks'].append(f'net{idx}')
            idx += 1
    if 'volumes' in toml:
        data_folder = pathlib.Path('/'.join(str(core.path.data).split('/')[:-1])) / toml['name'] 
        log_folder = pathlib.Path('/'.join(str(core.path.log).split('/')[:-1])) / toml['name'] 
        temp_folder = pathlib.Path('/'.join(str(core.path.temp).split('/')[:-1])) / toml['name']
        base_config_folder = core.path.lcars / 'config'
        config_folder = base_config_folder / toml['name']
        comp['services'][toml['name']]['volumes'] = []
        if 'config' in toml['volumes']:
            for entry in toml['volumes']['config']:
                source = entry['source']
                source = source.replace('%data_folder%', str(data_folder))
                source = source.replace('%log_folder%', str(log_folder))
                source = source.replace('%temp_folder%', str(temp_folder))
                source = source.replace('%base_folder%', str(core.path.base))
                source = source.replace('%base_config_folder%', str(base_config_folder))
                source = source.replace('%config_folder%', str(config_folder))
                if not pathlib.Path(source).exists():
                    p = await asyncio.subprocess.create_subprocess_shell(
                        f'mkdir -p {str(config_folder)}', 
                        stderr=asyncio.subprocess.PIPE, 
                        stdout=asyncio.subprocess.PIPE)
                    await p.wait()
                    base = entry['base']
                    base = base.replace('%data_folder%', str(data_folder))
                    base = base.replace('%log_folder%', str(log_folder))
                    base = base.replace('%temp_folder%', str(temp_folder))
                    base = base.replace('%base_folder%', str(core.path.base))
                    base = base.replace('%base_config_folder%', str(base_config_folder))
                    base = base.replace('%config_folder%', str(config_folder))
                    p = await asyncio.subprocess.create_subprocess_shell(
                        f'cp {base} {source}', 
                        stderr=asyncio.subprocess.PIPE, 
                        stdout=asyncio.subprocess.PIPE)
                    await p.wait()
                comp['services'][toml['name']]['volumes'].append(f"{source}:{entry['dest']}:ro")
        if 'data' in toml['volumes']:
            for source, dest in toml['volumes']['data'].items():
                source = source.replace('%data_folder%', str(data_folder))
                source = source.replace('%log_folder%', str(log_folder))
                source = source.replace('%temp_folder%', str(temp_folder))
                source = source.replace('%base_folder%', str(core.path.base))
                source = source.replace('%base_config_folder%', str(base_config_folder))
                comp['services'][toml['name']]['volumes'].append(f"{source}:{dest}")
    if 'restart' in toml:
        comp['services'][toml['name']]['restart'] = toml['restart']
    comp['services'][toml['name']]['labels'] = ["pro.holler.lcars.managed=true"]
    await aioyamllib.dump(core.path.temp / f'compose/{toml["name"]}.yml', comp)    
    cmd = f'docker compose -f {str(core.path.temp)}/compose/{toml["name"]}.yml up -d'
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
        
async def restart_container(name: str) -> None:
    cmd = f'docker container restart {name}'
    print(cmd)
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
        

async def main() -> None:
    core = corelib.Core()
    await core.add('const', constlib.Const)
    await core.add('path', sv_pathlib.Path, pathlib.Path(sys.argv[2]) / 'data' / 'supervisor' / 'folder.yml')
    await core.add('cfg', configlib.Config, toml=core.path.config / core.const.hostname / 'config.toml',
                                            acl=core.path.lcars / 'config/acl.toml')
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
        if (cont_data := await core.docker.containers.get(container)) is None:
            await container_add(core, container)
            return
        else:
            if cont_data.status != "running":
                await restart_container(container)
            elif (state := cont_data.attrs['State'].get('Health', {}).get('Status')) is not None:
                if state == 'unhealthy':
                    await restart_container(container)
    for container in await core.docker.containers.list():
        if 'pro.holler.lcars.managed' in container.labels:
            if container.name not in container_data.get('apps', []):
                await core.const.loop.run_in_executor(None, container.stop)
                await core.const.loop.run_in_executor(None, partial(container.remove, force=True)) 
                return

if __name__ == "__main__":
    asyncio.run(main())
