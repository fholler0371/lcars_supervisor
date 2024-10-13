import asyncio

import corelib

async def main() -> None:
    core = corelib.DockerCore()
    await core.run_it()

if __name__ == '__main__':
    asyncio.run(main())
    