import sys
sys.path.append('/lcars/lib')
import asyncio

import corelib
import constlib
import aiopathlib
import configlib
import loggerlib
import signallib

import time


async def main() -> None:
    core = corelib.Core()
    await core.add('path', aiopathlib.Path)
    await core.add('const', constlib.Const)
    await core.add('cfg', configlib.Config, toml=core.path.config / 'config.toml')
    await core.add('log', loggerlib.Logger)
    await core.add('running', asyncio.Event())
    await core.add('signal', signallib.Signal)
    core.log.info(f'starte {core.const.app} (pid: {core.const.pid})')
    await core.running.wait()
    core.log.info(f'stoppe {core.const.app}')
    await asyncio.sleep(3)
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
    