import asyncio
import tomllib


def _loader(file_name: str) -> None:
        try:
            with file_name.open('rb') as f:
                return tomllib.load(f)
        except:
            return None

async def loader(file_name: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _loader, file_name)
