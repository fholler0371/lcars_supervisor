from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QuerySingle, QueryInsert, QueryUpdate

class RefreshToken(Table):
    def __init__(self):
        super().__init__('refresh_token')
        self.add_field(Text('token'))
        self.add_field(Text('data'))
        self.add_field(Integer('timestamp'))
        #
        self.add_statement('delete', QueryInsert("DELETE FROM {table} WHERE timestamp<?", 
                                                 ['timestamp']))
        self.add_statement('insert', QueryInsert("INSERT INTO {table} (token, data, timestamp) VALUES (?, ?, ?)", 
                                                 ['token', 'data', 'timestamp']))
        self.add_statement('data', QuerySingle("SELECT {fields} FROM {table} WHERE token=?", ['data'], ['token']))