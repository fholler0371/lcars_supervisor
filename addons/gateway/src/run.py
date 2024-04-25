import asyncio

import corelib

import time


async def main() -> None:
    core = corelib.DockerCore()
    await core.run_it()

    core.log.info(f'starte {core.const.app} (pid: {core.const.pid})')
    await core.start()
    await core.running.wait()
    await core.stop()
    core.log.info(f'stoppe {core.const.app}')
    

if __name__ == '__main__':
    asyncio.run(main())

time.sleep(100)
print('is_running end x1', flush=True)
    