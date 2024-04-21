import sys
sys.path.append('/lcars/lib')

import asyncio

import time
import os

import corelib
import constlib
import aiopathlib
import signallib


async def main() -> None:
    core = corelib.Core()
    await core.add('const', constlib.Const)
    await core.add('path', aiopathlib.Path)
    await core.add('running', asyncio.Event())
    await core.add('signal', signallib.Signal)
    updater = await asyncio.subprocess.create_subprocess_shell(f'python {core.path.base}/starter/update.py')
    await updater.wait()
    run = await asyncio.subprocess.create_subprocess_shell(f'python {core.path.base}/starter/run.py')
    await core.running.wait()
    try:
        with open(constlib.DOCKER_PIDFILE) as f:
            os.kill(int(f.read()), 15)
    except Exception as e:
        print(e, flush=True)
    await run.wait()

if __name__ == '__main__':
    asyncio.run(main())
