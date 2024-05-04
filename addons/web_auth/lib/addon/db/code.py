from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QuerySingle, QueryInsert, QueryUpdate

class Code(Table):
    def __init__(self):
        super().__init__('code')
        self.add_field(Text('code'))
        self.add_field(Text('data'))
        self.add_field(Integer('timestamp'))
        #
        self.add_statement('delete', QueryInsert("DELETE FROM {table} WHERE timestamp<?", 
                                                 ['timestamp']))
        self.add_statement('insert', QueryUpdate("INSERT INTO {table} (code, data, timestamp) VALUES (?, ?, ?)", 
                                                 ['code', 'data', 'timestamp']))
