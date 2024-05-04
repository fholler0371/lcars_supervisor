from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QueryMulti, QuerySingle, QueryInsert

class App(Table):
    def __init__(self):
        super().__init__('app')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('name'))
        self.add_field(Text('type'))
        #
        self.add_statement('get_app', QuerySingle("SELECT {fields} FROM {table} WHERE name=?", ['id', 'type'], ['name']))        
        self.add_statement('insert', QueryInsert("INSERT INTO {table} (name, type) VALUES (?, ?)", 
                                                 ['name', 'type']))
        
class Oauth(Table):
    def __init__(self):
        super().__init__('oauth')
        self.add_field(Integer('app_id'))
        self.add_field(Text('clientid'))
        self.add_field(Text('secret'))
        self.add_field(Text('callback'))
        #
        self.add_statement('get_client_data', QuerySingle("SELECT {fields} FROM {table} WHERE app_id=?", ['clientid', 'secret', 'callback'], ['app_id']))        
        self.add_statement('insert', QueryInsert("INSERT INTO {table} (app_id, clientid, secret, callback) VALUES (?, ?, ?, ?)", 
                                                 ['app_id', 'clientid', 'secret', 'callback']))