from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text, Float
from aiodatabase.statements import QueryMulti, QuerySingle, QueryUpdate, QueryDelete, QueryInsert

class Vital(Table):
    def __init__(self):
        super().__init__('vital')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Integer('date'))
        self.add_field(Text('type'))
        self.add_field(Float('value'))
        #
        self.add_statement('get_last_by_type', QuerySingle("SELECT {fields} FROM {table} WHERE type=? ORDER BY date DESC", 
                                                           ['value'], ['type']))
        self.add_statement('get_history', QueryMulti("SELECT {fields} FROM {table} WHERE type=? and date>? ORDER BY date DESC", 
                                                           ['value', 'date'], ['type', 'date']))
        self.add_statement('get_avg', QuerySingle("SELECT avg(value) as {fields} FROM {table} WHERE date>? and type='gewicht' ORDER BY date DESC", 
                                                           ['value'], ['date']))
        
        
        
                
        self.add_statement('get_500', QueryMulti("SELECT {fields} FROM {table} ORDER BY date DESC LIMIT 500", 
                                                 ['id', 'date', 'name', 'amount', 'count']))    
        self.add_statement('edit', QueryUpdate("UPDATE {table} SET date=?, name=?, amount=?, count=? WHERE id=?", 
                                               ['date', 'name', 'amount', 'count', 'id']))        
        self.add_statement('delete', QueryDelete("DELETE FROM {table} WHERE id=?", ['id']))        
        self.add_statement('add', QueryInsert("INSERT INTO {table} (date, name, amount, count) VALUES (?, ?, ?, ?)", 
                                              ['date', 'name', 'amount', 'count']))        
        self.add_statement('get_max_id', QuerySingle("SELECT max(id) as {fields} FROM {table}", ['id']))        
