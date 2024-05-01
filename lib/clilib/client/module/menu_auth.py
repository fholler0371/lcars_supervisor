class MenuAuth:
    def __init__(self, core):
        self.core = core
        self.step = 'main/auth'
        self.menu_entries = [
            {'label': 'Apps Status', 'action': 'main/docker/doc_status'},
            {'label': 'App hinzufügen', 'action': 'main/docker/doc_add'},
            {'label': 'App entfernen', 'action': 'main/docker/doc_remove'}
        ]
        self.table = None

    async def update_data(self):
        pass