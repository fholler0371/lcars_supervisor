class MenuMain:
    def __init__(self, core):
        self.core = core
        self.step = 'main'
        self.menu_entries = [
            {'label': 'Apps Status', 'action': 'main/doc_status'},
            {'label': 'App hinzufügen', 'action': 'main/doc_add'},
            {'label': 'App entfernen', 'action': 'main/doc_remove'}
        ]
        self.table = None

    async def update_data(self):
        pass