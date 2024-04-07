import sys
if __name__ == "__main__":
    sys.path.append(sys.argv[1]+'/lib')
import asyncio
import pathlib

import corelib
import constlib
import sv_pathlib
import configlib
import aiodockerlib


from pprint import pprint


async def check_network(core: corelib.Core, name: str, data: any) -> None:
    if (net := await core.docker.networks.get(name)) is not None:
        return
    match data["type"]:
        case 'bridge':
            p = await asyncio.subprocess.create_subprocess_shell(
                f'docker network create --attachable --ip-range {data["subnet"]} --subnet {data["subnet"]} --opt com.docker.network.bridge.name={data["adapter"]} ' + 
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
    
    
    #print(sys.path)
    #print(sys.argv)
    #print('dockerd')

if __name__ == "__main__":
    asyncio.run(main())
    
#docker network create --attachable --ip-range 10.1.0.0/16 
# --subnet 10.1.0.0/16 --opt com.docker.network.bridge.name=lcars1 --opt com.docker.network.container_iface_prefix=eth0 local-bridge