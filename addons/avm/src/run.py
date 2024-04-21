import sys
sys.path.append('/lcars/lib')
sys.path.append('/lcars/lib2')
import asyncio

import corelib
import constlib
import aiopathlib
import configlib
import loggerlib
import signallib
import httplib
import addon_com

import time


async def main() -> None:
    core = corelib.Core()
    await core.add('path', aiopathlib.Path)
    await core.add('const', constlib.Const)
    await core.add('cfg', configlib.Config, toml=core.path.config / 'config.toml')
    await core.add('log', loggerlib.Logger)
    await core.add('running', asyncio.Event())
    await core.add('signal', signallib.Signal)
    await core.add('web_l', httplib.ClientLocal)
    await core.add('com', addon_com.Com)
    core.log.info(f'starte {core.const.app} (pid: {core.const.pid})')
    await core.start()
    await core.running.wait()
    await core.stop()
    core.log.info(f'stoppe {core.const.app}')
    

if __name__ == '__main__':
    asyncio.run(main())

    