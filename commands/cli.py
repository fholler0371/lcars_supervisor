import asyncio
import pathlib
import sys
if __name__ == "__main__":
    sys.path.append(sys.argv[1]+'/lib')
    
import corelib
import constlib
import sv_pathlib
import configlib
import loggerlib
import clilib
import aiodockerlib
import httplib


from pprint import pprint

async def main() -> None:
    core = corelib.Core()
    await core.add('const', constlib.Const)
    await core.add('path', sv_pathlib.Path, pathlib.Path(sys.argv[2]) / 'data' / 'supervisor' / 'folder.yml')
    await core.path.replace_app('supervisor')
    await core.add('cfg', configlib.Config, toml=core.path.config / core.const.hostname / 'config.toml')
    await core.add('log', loggerlib.Logger)
    await core.add('docker', aiodockerlib.Docker)
    await core.add('web_l', httplib.ClientLocal)
    core.log.info('cli geladen')
    await core.add('cli_s', clilib.ClientCtrl)
    core.log.info('cli beendet')
    
if __name__ == "__main__":
    asyncio.run(main())