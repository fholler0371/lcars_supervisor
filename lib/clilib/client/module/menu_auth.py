class MenuAuth:
    def __init__(self, core):
        self.core = core
        self.step = 'main/auth'
        self.menu_entries = [
            {'label': 'Nutzer mit Passwort eintragen', 'action': 'main/auth/add'},
            {'label': 'App hinzufügen', 'action': 'main/docker/doc_add'},
            {'label': 'App entfernen', 'action': 'main/docker/doc_remove'}
        ]
        self.table = None

    async def update_data(self):
        pass