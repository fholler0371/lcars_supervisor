import aiofiles.os as os
from functools import partial
try:
    from rich.table import Table
except:
    pass
from datetime import datetime as dt

import clilib.data as cd

import time


class MenuDockerStatus:
    def __init__(self, core):
        self.core = core
        self.step = 'main/docker/doc_status'
        self.menu_entries = []
        self.table = None
    
    async def update_data(self):
        self.menu_entries.clear()
        self.table = None
        resp = await self.core.web_l.get('docker/status')
        if resp is None:
            return
        self.table = Table(show_header=True, header_style="bold magenta", title="Container Status")
        self.table.add_column("Name", width=20) #table.add_column("Date", style="dim", width=12)#
        self.table.add_column("Status", width=10) 
        self.table.add_column("Verwaltet", width=9, justify="center") 
        self.table.add_column("Python", width=6, justify="center") 
        self.table.add_column("Netzwerk", width=15) 
        self.table.add_column("IP-Adresse", width=15) 
        self.table.add_column("Erstellt", width=10, style="dim") 
        self.table.add_column("Start", width=20) 
        resp = [cd.CliStatus(**x) for x in resp]
        for entry in resp:
            state_color = 'yellow'
            if entry.status in ['running', 'healthy']:
                state_color = 'green'
            elif entry.status in ['exited', 'unhealthy']:
                state_color = 'red'
            self.table.add_row(entry.name, f"[{state_color}]{entry.status}[/{state_color}]", f"[red]{'ja' if entry.lcars else 'nein'}[/red]",
                               f"[red]{'ja' if entry.python else 'nein'}[/red]",
                               entry.network, f"[green]{entry.ip}[/green]",
                               dt.fromtimestamp(entry.created).strftime('%d.%m.%Y'),
                               dt.fromtimestamp(entry.start).strftime('%d.%m.%Y %H:%M:%S'))
    
    async def add_addons(self, name: str) -> None:
        await self.core.web_l.post('docker/deactivate', {'addon': name})
