import sys
sys.path.append('/lcars/lib')
import asyncio

import corelib
import constlib
import aiopathlib
import configlib

import time


async def main() -> None:
    core = corelib.Core()
    await core.add('path', aiopathlib.Path)
    await core.add('const', constlib.Const)
    await core.add('cfg', configlib.Config, toml=core.path.config / 'config.toml')
    print(core)
    print(core.const.is_docker)
    print(core.const.app)
    print(core.path.config)
    print(core.const.hostname)
    print(core.cfg.toml)
    print('web_base', flush=True)
    

if __name__ == '__main__':
    asyncio.run(main())

time.sleep(100)
print('is_running end x1', flush=True)
    