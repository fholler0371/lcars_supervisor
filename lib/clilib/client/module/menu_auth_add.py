import aiofiles.os as os
try:
    from rich.console import Console
except:
    pass
import aiotomllib
import aioyamllib
from functools import partial
import pathlib
import time

import clilib.data as cd
from aioauth.models import UserData

class MenuAuthAdd:
    def __init__(self, core):
        self.core = core
        self.step = 'main/auth/add'
        self.menu_entries = []
        self.table = None
        
    async def update_data(self):
        self.menu_entries.clear()
        console = Console()
        console.clear()
        data = UserData(name=console.input(prompt="Nutzername:      "),
                        roles=console.input(prompt="Rollen:          "),
                        roles_secure=console.input(prompt="Rollen (sicher): "),
                        apps=console.input(prompt="Apps:            "),
                        apps_secure=console.input(prompt="Apps (sicher):   "),
                        password=console.input(prompt="Passwort:        ", password=True))
        await self.core.web_l.post('auth/add_user', data.model_dump(), dest='gateway_ip')
