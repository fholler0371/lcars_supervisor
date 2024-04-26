import asyncio

import corelib

import time


async def main() -> None:
    core = corelib.DockerCore()
    await core.run_it()    

if __name__ == '__main__':
    asyncio.run(main())

    