from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text, Float
from aiodatabase.statements import QuerySingle, QueryInsert, QueryUpdate

class PowerHist(Table):
    def __init__(self):
        super().__init__('history')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Integer('tstamp'))
        self.add_field(Text('label'))
        self.add_field(Float('value'))
        #
        self.add_statement('get_id', QuerySingle("SELECT {fields} FROM {table} WHERE tstamp=? and label=?", ['id'], ['tstamp', 'label']))    
        self.add_statement('insert', QueryInsert("INSERT INTO {table} (tstamp, label, value) VALUES (?, ?, ?)", 
                                                 ['tstamp', 'label', 'value']))
        self.add_statement('update', QueryUpdate("UPDATE {table} SET value=? WHERE id=?", 
                                                 ['value', 'id']))
        self.add_statement('get_last', QuerySingle("SELECT max(tstamp) as {fields} FROM {table} ORDER BY 'tstamp' asc LIMIT 1", ['tstamp']))
        self.add_statement('get_first', QuerySingle("SELECT min(tstamp) as {fields} FROM {table} ORDER BY 'tstamp' asc LIMIT 1", ['tstamp']))

