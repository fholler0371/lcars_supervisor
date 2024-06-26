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
import signallib
import httplib
import clilib


async def main() -> None:
    core = corelib.Core()
    await core.add('const', constlib.Const)
    await core.add('path', sv_pathlib.Path, pathlib.Path(sys.argv[2]) / 'data' / 'supervisor' / 'folder.yml')
    await core.add('cfg', configlib.Config, toml=core.path.config / core.const.hostname / 'config.toml',
                                            acl=core.path.lcars / 'config/acl.toml')
    await core.add('log', loggerlib.Logger)
    await core.add('running', asyncio.Event())
    await core.add('signal', signallib.Signal) 
    await core.add('docker', aiodockerlib.Docker)
    await core.add('web', httplib.HTTP, sv=True)
    await core.add('cli_s', clilib.Server)
    core.log.info(f'alles geladen, wird Hauptschleife startet ({core.const.pid})')
    await core.running.wait()
    core.log.info('Hauptschleife beendet')
    await core.const._astop()
    await core.web._astop()
    return core.const.reload

async def reload_loop() -> None:
    if await main():
        cmd = sys.executable + ' ' + ' '.join(sys.argv) + ' &'
        await asyncio.subprocess.create_subprocess_shell(cmd)

if __name__ == "__main__":
    asyncio.run(reload_loop())
    