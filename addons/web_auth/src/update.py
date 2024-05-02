import asyncio
import importlib

LIBS = {
   "cryptography" : "cryptography",
   "aiosqlite" : "aiosqlite",
   "bcrypt" : "bcrypt"
}

async def main() -> None:
    for _import, _check in LIBS.items():
        try:
            mod = importlib.import_module(_check)
        except:
            cmd = f'pip install {_import}'
            p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                                stderr=asyncio.subprocess.PIPE, 
                                                                stdout=asyncio.subprocess.PIPE)
            await p.wait()
            print(f'{_import} wurde installiert')

if __name__ == '__main__':
    asyncio.run(main())