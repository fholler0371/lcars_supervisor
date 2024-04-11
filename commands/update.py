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
    if len(entries := core.cfg.toml.get('systemend', [])) > 0:
        for entry in entries:
            await create_systemend(core, entry)
    await acivate_docker()
 
if __name__ == "__main__":
    asyncio.run(main())
    
    