import asyncio
import yaml


def _dump(file_name: str, data: dict) -> None:
        try:
            with file_name.open('w') as f:
                return yaml.dump(data, f)
        except:
            return None

async def dump(file_name: str, data: dict) -> None:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _dump, file_name, data)
