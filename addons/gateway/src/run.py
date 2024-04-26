import asyncio

import corelib

import time


async def main() -> None:
    core = corelib.DockerCore()
    await core.run_it()

if __name__ == '__main__':
    asyncio.run(main())

time.sleep(100)
print('is_running end x1', flush=True)
    