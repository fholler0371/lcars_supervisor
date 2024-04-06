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
    data_folder = pathlib.Path(LCARS_FOLDER) / 'data' / 'supervisor'
    p = await asyncio.subprocess.create_subprocess_shell(f'mkdir -p {str(data_folder)}', 
                                                             stderr=asyncio.subprocess.PIPE, 
                                                             stdout=asyncio.subprocess.PIPE)
    await p.wait()
    folder_file = data_folder / 'folder.yml'
    if folder_file.exists():
        with folder_file.open() as f:
            data = yaml.safe_load(f)
    else:
        data = {}
    data['base'] = str(BASE_FOLDER)
    data['lcars'] = str(LCARS_FOLDER)
    data['data'] = str(data_folder)
    with folder_file.open('w') as f:
        yaml.dump(data, f)
    cmd_folder = pathlib.Path(LCARS_FOLDER) / 'commands' 
    p = await asyncio.subprocess.create_subprocess_shell(f'mkdir -p {str(cmd_folder)}', 
                                                             stderr=asyncio.subprocess.PIPE, 
                                                             stdout=asyncio.subprocess.PIPE)
    if not (BASE_FOLDER / "commands").exists():
        p = await asyncio.subprocess.create_subprocess_shell(f'ln -s  {BASE_FOLDER / ".git/lcars_supervisor/commands"} {BASE_FOLDER / "commands"}', 
                                                                stderr=asyncio.subprocess.PIPE, 
                                                                stdout=asyncio.subprocess.PIPE)
        await p.wait()
    with (cmd_folder / 'update.sh').open('w') as f:
        f.write('#!/usr/bin/bash\n\ncd '+ str(BASE_FOLDER) + '\n\n' + sys.executable + f' {BASE_FOLDER / "commands" / "update_pre.py"} {LCARS_FOLDER}'+ '\n')
        f.write(sys.executable + f' {BASE_FOLDER / "commands" / "update.py"} {LCARS_FOLDER}'+ '\n')
    p = await asyncio.subprocess.create_subprocess_shell(f'chmod +x {cmd_folder / "update.sh"}', 
                                                             stderr=asyncio.subprocess.PIPE, 
                                                             stdout=asyncio.subprocess.PIPE)
    await p.wait()
    p = await asyncio.subprocess.create_subprocess_shell(f'rm /usr/bin/lcars-sv-update', 
                                                             stderr=asyncio.subprocess.PIPE, 
                                                             stdout=asyncio.subprocess.PIPE)
    await p.wait()
    p = await asyncio.subprocess.create_subprocess_shell(f'sudo ln -s {cmd_folder / "update.sh"} /usr/bin/lcars-sv-update', 
                                                             stderr=asyncio.subprocess.PIPE, 
                                                             stdout=asyncio.subprocess.PIPE)
    await p.wait()
    p = await asyncio.subprocess.create_subprocess_shell('lcars-sv-update')
    await p.wait()
    
            
if __name__ == '__main__' and RUN == 1:
    asyncio.run(part_a())

if __name__ == '__main__' and RUN == 2:
    import yaml
    asyncio.run(part_b())
