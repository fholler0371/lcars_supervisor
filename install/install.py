import sys
import pathlib
import asyncio

BASE_FOLDER = pathlib.Path(sys.argv[1])
LCARS_FOLDER = sys.argv[2]
RUN = 1 if len(sys.argv) < 4 else int(sys.argv[3])

async def part_a() -> None:
    if not (BASE_FOLDER / '.venv').exists():
        cmd = f'python3 -m venv {BASE_FOLDER / ".venv"}'
        p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                             stderr=asyncio.subprocess.PIPE, 
                                                             stdout=asyncio.subprocess.PIPE)
        await p.wait()
    cmd = f'{BASE_FOLDER / ".venv/bin/pip3 install pyyaml aiohttp aiofiles aiosignal"}'
    p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                         stderr=asyncio.subprocess.PIPE, 
                                                         stdout=asyncio.subprocess.PIPE)
    await p.wait() 
    cmd = f'{BASE_FOLDER / ".venv/bin/python3"} {" ".join(sys.argv)} 2'
    p = await asyncio.subprocess.create_subprocess_shell(cmd)
    await p.wait() 
    
async def part_b() -> None:
    print(RUN)
    print(BASE_FOLDER)
    print(LCARS_FOLDER)
    print(yaml)
            
if __name__ == '__main__' and RUN == 1:
    asyncio.run(part_a())

if __name__ == '__main__' and RUN == 2:
    import yaml
    asyncio.run(part_b())
