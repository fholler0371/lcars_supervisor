import time

from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QuerySingle, QueryInsert, QueryMulti, QueryUpdate

class Scopes(Table):
    def __init__(self):
        super().__init__('scopes')
        self.add_field(Text('label'))
        self.add_field(Integer('timestamp'))
        #
        self.add_statement('get_timestamp', QuerySingle("SELECT {fields} FROM {table} WHERE label=?", ['timestamp'], ['label']))    
        self.add_statement('insert', QueryInsert("INSERT INTO {table} (label, timestamp) VALUES (?, ?)", 
                                                 ['label', 'timestamp']))
        self.add_statement('update', QueryUpdate("UPDATE {table} SET timestamp=? WHERE label=?", 
                                                 ['timestamp', 'label']))
        self.add_statement('get_all', QueryMulti('SELECT {fields} from {table} WHERE timestamp>?', ['label'], ['timestamp']))

