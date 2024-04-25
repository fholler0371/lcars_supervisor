import asyncio
import yaml
import pathlib


def _dump(file_name: pathlib.Path, data: dict) -> None:
    with file_name.open('w') as f:
        return yaml.dump(data, f)

async def dump(file_name: pathlib.Path, data: dict) -> None:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _dump, file_name, data)
