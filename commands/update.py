import sys
if __name__ == "__main__":
    sys.path.append('/'.join(sys.argv[0].split('/')[:-2])+'/lib')
import asyncio
import pathlib
import aioretry

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

async def main() -> None:
    core = corelib.Core()
    await core.add('const', constlib.Const)
    await core.add('path', sv_pathlib.Path, pathlib.Path(sys.argv[1]) / 'data' / 'supervisor' / 'folder.yml')
    await core.add('cfg', configlib.Config, toml=core.path.config / core.const.hostname / 'config.toml')
    if len(packages := core.cfg.toml.get('install', {}).get('apt', [])) > 0:
        for package in core.cfg.toml.get('install', {}).get('apt', []):
            print('.', end='', flush=True)
            await apt_install(package)
        print()
    await acivate_docker()
 
if __name__ == "__main__":
    asyncio.run(main())
    
    