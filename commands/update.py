import sys
if __name__ == "__main__":
    sys.path.append('/'.join(sys.argv[0].split('/')[:-2])+'/lib')
import asyncio
import pathlib
import aioretry
import tempfile
import os

import corelib
import constlib
import sv_pathlib
import configlib

MAX_RETRY = 10
def retry_policy(info: aioretry.RetryInfo) -> aioretry.RetryPolicyStrategy:
    return info.fails > MAX_RETRY, (2 ** info.fails) * 0.1

@aioretry.retry(retry_policy)
async def apt_install(package: str) -> None:
    p = await asyncio.subprocess.create_subprocess_shell(
                      f'sudo apt-get install {package} -y', 
                      stderr=asyncio.subprocess.PIPE, 
                      stdout=asyncio.subprocess.PIPE)
    out, err = await p.communicate()
    if err.decode() != '':
        raise Exception
    
async def acivate_docker() -> None:
    p = await asyncio.subprocess.create_subprocess_shell('docker --version', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    await p.wait()
    if p.returncode != 0:
        p = await asyncio.subprocess.create_subprocess_shell('curl -sSL https://get.docker.com | sudo sh', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.wait()
        p = await asyncio.subprocess.create_subprocess_shell('sudo systemctl enable docker.service', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.wait()
        p = await asyncio.subprocess.create_subprocess_shell('sudo systemctl enable containerd.service', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        await p.wait()
    p = await asyncio.subprocess.create_subprocess_shell('sudo groupadd docker', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    await p.wait()
    p = await asyncio.subprocess.create_subprocess_shell('sudo usermod -aG docker $USER', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    await p.wait()
    p = await asyncio.subprocess.create_subprocess_shell('sudo chmod 666 /var/run/docker.sock', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    await p.wait()
    
async def create_systemend(core: corelib.Core, entry: dict) -> None:
    if entry.get('start', False):
        p = await asyncio.subprocess.create_subprocess_shell(f'sudo systemctl stop {entry["name"]}', 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
        await p.wait()
    content = entry['content'].replace('%python%', sys.executable).replace('%base%', str(core.path.base)).replace('%lcars%', str(core.path.lcars))
    name = ''
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content.encode())
        name = f.name
    p = await asyncio.subprocess.create_subprocess_shell(f'sudo cp {name} /etc/systemd/system/{entry["name"]}', 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
    await p.wait()
    os.unlink(name)
    if entry.get('start', False):
        p = await asyncio.subprocess.create_subprocess_shell(f'sudo systemctl start {entry["name"]}', 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
        await p.wait()
    if entry.get('enable', False):
        p = await asyncio.subprocess.create_subprocess_shell(f'sudo systemctl enable {entry["name"]}', 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
        await p.wait()
        
async def reload_systemend() -> None:
    p = await asyncio.subprocess.create_subprocess_shell('sudo systemctl daemon-reload', 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
    await p.wait()
    
async def install_app(core: dict, app: str, cmd_name: str) -> None:
    sh_file = core.path.lcars / 'commands' / f'{app}.sh'
    with sh_file.open('w') as f:
        f.write('#!/usr/bin/bash\n\ncd ')
        f.write(str(core.path.base))
        f.write('\n\n')
        f.write(f'{sys.executable} {core.path.base}/commands/{app}.py {core.path.base} {core.path.lcars}')
        f.write('\n')
    cmd = f'chmod +x {sh_file}'
    p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
    await p.wait()
    cmd = f'sudo ln -s {sh_file} /usr/bin/{cmd_name}'
    p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
    await p.wait()

async def install_config(core: dict, source: str, dest: str) -> None:
    dest_file = core.path.lcars / dest.replace('%hostname%', core.const.hostname)
    if dest_file.exists():
        return #Config wird nicht überschrieben
    cmd = f"mkdir -p {'/'.join(str(dest_file).split('/')[:-1])}"
    p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
    await p.wait()
    cmd = f"cp {core.path.base}/.git/lcars_supervisor/config/{source} {dest_file}"
    p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                        stderr=asyncio.subprocess.PIPE, 
                                                        stdout=asyncio.subprocess.PIPE)
    await p.wait()

async def main() -> None:
    core = corelib.Core()
    await core.add('const', constlib.Const)
    await core.add('path', sv_pathlib.Path, pathlib.Path(sys.argv[1]) / 'data' / 'supervisor' / 'folder.yml')
    await core.add('cfg', configlib.Config, toml=core.path.config / core.const.hostname / 'config.toml')
    if len(packages := core.cfg.toml.get('install', {}).get('apt', [])) > 0:
        for package in packages:
            print('.', end='', flush=True)
            await apt_install(package)
        print()
    if len(apps := core.cfg.toml.get('install', {}).get('apps', [])) > 0:
        for app, label in apps.items():
            await install_app(core, app, label)
    if len(entries := core.cfg.toml.get('install', {}).get('config', [])) > 0:
        for source, dest in entries.items():
            await install_config(core, source, dest)
    if len(entries := core.cfg.toml.get('systemd', [])) > 0:
        for entry in entries:
            await create_systemend(core, entry)
    await reload_systemend()
    await acivate_docker()

if __name__ == "__main__":
    asyncio.run(main())