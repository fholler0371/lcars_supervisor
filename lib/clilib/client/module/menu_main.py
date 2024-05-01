class MenuMain:
    def __init__(self, core):
        self.core = core
        self.step = 'main'
        self.menu_entries = [
            {'label': 'Docker', 'action': 'main/docker'},
            {'label': 'Nutzer', 'action': 'main/auth'}#,
            #{'label': 'App entfernen', 'action': 'main/doc_remove'}
        ]
        self.table = None

    async def update_data(self):
        pass