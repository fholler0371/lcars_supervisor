import asyncio


async def main() -> None:
    try:
        import cryptography.hazmat
    except:
        cmd = 'pip install cryptography'
        p = await asyncio.subprocess.create_subprocess_shell(cmd, 
                                                            stderr=asyncio.subprocess.PIPE, 
                                                            stdout=asyncio.subprocess.PIPE)
        await p.wait()
        print('cryptography wurde installiert')

if __name__ == '__main__':
    asyncio.run(main())