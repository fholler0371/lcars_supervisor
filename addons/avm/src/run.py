import asyncio

import corelib
import constlib
import configlib
import loggerlib
import signallib
import httplib
import addon_com

import time


async def main() -> None:
    core = corelib.DockerCore()
    await core.run_it()
    
    await core.add('const', constlib.Const)
    await core.add('cfg', configlib.Config, toml=core.path.config / 'config.toml',
                                            acl=core.path.config / 'acl.toml')
    await core.add('log', loggerlib.Logger)
    await core.add('running', asyncio.Event())
    await core.add('signal', signallib.Signal)
    await core.add('web', httplib.HTTP)
    await core.add('web_l', httplib.ClientLocal)
    await core.add('com', addon_com.Com)
    core.log.info(f'starte {core.const.app} (pid: {core.const.pid})')
    await core.start()
    await core.running.wait()
    await core.stop()
    core.log.info(f'stoppe {core.const.app}')
    

if __name__ == '__main__':
    asyncio.run(main())

    