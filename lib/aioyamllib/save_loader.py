import asyncio
import yaml


def _safe_load(file_name: str) -> None:
        try:
            with file_name.open() as f:
                return yaml.safe_load(f)
        except:
            return None

async def save_load(file_name: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _safe_load, file_name)
