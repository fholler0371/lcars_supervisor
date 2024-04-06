import sys
import pathlib
import asyncio
import yaml
import socket
import tomllib

async def load_config(base: str, folder: str) -> dict:
    hostname = socket.getfqdn()
    file = pathlib.Path(folder) / hostname / 'config.yml'
    if not file.exists():
        p = await asyncio.subprocess.create_subprocess_shell(
                      f'mkdir -p {pathlib.Path(folder) / hostname} ; cp {pathlib.Path(base) / ".git/lcars_supervisor/config/config.toml"} {file}', 
                      stderr=asyncio.subprocess.PIPE, 
                      stdout=asyncio.subprocess.PIPE)
        await p.wait()
    with file.open('rb') as f:
        return tomllib.load(f)

async def load_folder(file: pathlib.Path) -> dict: 
    with file.open() as f:
        folder = yaml.safe_load(f)
    change = False
    if 'config' not in folder:
        folder['config'] = folder['lcars'] + '/config/supervisor'
        change = True
    if change:
        with file.open('w') as f:
            yaml.dump(folder, f)
    return folder

async def clone(base: str) -> None: 
    folder = pathlib.Path(base) / '.git' / 'lcars_supervisor'
    p = await asyncio.subprocess.create_subprocess_shell(
                f'cd {folder} ; git pull', 
                stderr=asyncio.subprocess.PIPE, 
                stdout=asyncio.subprocess.PIPE)
    await p.wait()

async def link_folder(base: str, folder: str) -> None:
    source = pathlib.Path(base) / '.git' / 'lcars_supervisor' / folder
    dest = pathlib.Path(base) / folder
    if not dest.exists():
        p = await asyncio.subprocess.create_subprocess_shell(f'ln -s {source} {dest}', 
                                                                stderr=asyncio.subprocess.PIPE, 
                                                                stdout=asyncio.subprocess.PIPE)
        await p.wait()

async def main() -> None:
    folder = await load_folder(pathlib.Path(sys.argv[1]) / 'data/supervisor/folder.yml')
    cfg = await load_config(folder['base'], folder['config'])
    if cfg.get('pre', {}).get('pull', False):
        await clone(folder['base'])
    for folder_ln in cfg.get('pre', {}).get('folder_ln', []):
        await link_folder(folder['base'], folder_ln)

if __name__ == "__main__":
    asyncio.run(main())