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
    core = corelib.DockerCore()
    await core.run_it()

if __name__ == '__main__':
    asyncio.run(main())
    