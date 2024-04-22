try:
    from simple_term_menu import TerminalMenu
    from rich import console as con
    from rich.console import Console
except:
    pass
import time

from corelib import BaseObj, Core

from .module import MenuMain, MenuDockerAdd, MenuDockerRemove, MenuDockerStatus


class ClientCtrl(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._steps = {}
        self._con = con.Console()
        self._rich = Console()
        
    async def show_menu(self, page) -> any:
        menu = []
        idx = 1
        for entry in page.menu_entries:
            menu.append(f'[{idx}] {entry["label"]}')
            idx += 1
        if menu:
            menu.append('')
        menu.append('[z] zurück')
        try:
            terminal_menu = TerminalMenu(menu, skip_empty_entries=True, 
                                         cycle_cursor=False,
                                         shortcut_key_highlight_style= ('fg_yellow', "bold"),
                                         title="Menü")
        except Exception as e:
            print(e)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index+1 == len(menu):
            return -1 
        else:
            return page.menu_entries[menu_entry_index]['action']
                
    async def _ainit(self):
        self.add_entry(MenuMain(self.core))
        self.add_entry(MenuDockerAdd(self.core))
        self.add_entry(MenuDockerRemove(self.core))
        self.add_entry(MenuDockerStatus(self.core))
        step = 'main'
        while step != '':
            page = self._steps[step]
            try:
                await page.update_data()
                self._con.clear()
                if page.table:
                    self._rich.print(page.table)
            except Exception as e:
                print(e)
            next = await self.show_menu(page)
            if next == -1:
                step =  '/'.join(step.split('/')[:-1])
            elif isinstance(next, str):
                step = next
            else:
                try:
                    await next()
                except Exception as e:
                    self.core.log.error(e)

    def add_entry(self, entry: any) -> None:
        self._steps[entry.step] = entry
