from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QueryMulti, QuerySingle, QueryUpdate, QueryDelete, QueryInsert

class Bought(Table):
    def __init__(self):
        super().__init__('bought')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('date'))
        self.add_field(Text('name'))
        self.add_field(Integer('amount'))
        self.add_field(Integer('count'))
        #
        self.add_statement('get_sum', QuerySingle("SELECT sum(amount) as {fields} FROM {table}", 
                                                         ['amount']))        
        self.add_statement('get_500', QueryMulti("SELECT {fields} FROM {table} ORDER BY date DESC LIMIT 500", 
                                                 ['id', 'date', 'name', 'amount', 'count']))    
        self.add_statement('edit', QueryUpdate("UPDATE {table} SET date=?, name=?, amount=?, count=? WHERE id=?", 
                                               ['date', 'name', 'amount', 'count', 'id']))        
        self.add_statement('delete', QueryDelete("DELETE FROM {table} WHERE id=?", ['id']))        
        self.add_statement('add', QueryInsert("INSERT INTO {table} (date, name, amount, count) VALUES (?, ?, ?, ?)", 
                                              ['date', 'name', 'amount', 'count']))        
        self.add_statement('get_max_id', QuerySingle("SELECT max(id) as {fields} FROM {table}", ['id']))        
    
    
    
