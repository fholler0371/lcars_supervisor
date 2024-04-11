import asyncio
import pathlib
import sys
if __name__ == "__main__":
    sys.path.append(sys.argv[1]+'/lib')

import corelib
import constlib
import sv_pathlib
import configlib
import aiodockerlib
import loggerlib

async def main() -> None:
    core = corelib.Core()
    await core.add('const', constlib.Const)
    await core.add('path', sv_pathlib.Path, pathlib.Path(sys.argv[2]) / 'data' / 'supervisor' / 'folder.yml')
    await core.add('cfg', configlib.Config, toml=core.path.config / core.const.hostname / 'config.toml')
    await core.add('log', loggerlib.Logger)
    await core.add('running', asyncio.Event())
    await core.add('docker', aiodockerlib.Docker)
    core.log.info('alles geladen, wird Hauptschleife startet')
    await asyncio.sleep(70)
    core.log.info('Hauptschleife beendet')
    print('exit')

if __name__ == "__main__":
    asyncio.run(main())
    