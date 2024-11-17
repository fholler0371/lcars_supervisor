from aiodatabase.tables import Table
from aiodatabase.fields import Integer, Text
from aiodatabase.statements import QueryMulti, QuerySingle, QueryInsert, QueryUpdate, QueryDelete

class Category(Table):
    def __init__(self):
        super().__init__('category')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('label'))
        self.add_field(Integer('activ'))
        self.add_field(Integer('days'))
        #
        self.add_statement('get_all', QueryMulti("SELECT {fields} FROM {table} order by label", ['id', 'label', 'activ', 'days']))        
        self.add_statement('add_new', QueryInsert("INSERT INTO {table} ('label', 'activ', 'days') VALUES (?, ?, ?)", ['label', 'activ', 'days']))        
        self.add_statement('get_last', QuerySingle("SELECT {fields} FROM {table} ORDER BY id DESC LIMIT 1", ['id', 'label', 'activ', 'days']))        
        self.add_statement('update', QueryUpdate("UPDATE {table} SET label=?, activ=?, days=? WHERE id=?", ['label', 'activ', 'days', 'id']))        

class Budgets(Table):
    def __init__(self):
        super().__init__('budgets')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Integer('category'))
        self.add_field(Text('start'))
        self.add_field(Text('end'))
        self.add_field(Integer('amount'))
        #
        self.add_statement('get_by_category', QueryMulti("SELECT {fields} FROM {table} where category=? order by end", 
                                                         ['id', 'category', 'start', 'end', 'amount'],['category']))        
        self.add_statement('get_with_order', QueryMulti("SELECT {fields} FROM {table} order by end desc", 
                                                         ['id', 'category', 'start', 'end', 'amount']))    
        self.add_statement('edit', QueryUpdate("UPDATE {table} SET category=?, start=?, end=?, amount=? WHERE id=?", ["category", "start", "end", "amount", "id"])) 
        self.add_statement('id_new', QuerySingle("SELECT {fields} FROM {table} WHERE start='2000-01-01'", ['id']))
        self.add_statement('add_new', QueryInsert("INSERT INTO {table} (category, start, end, amount) VALUES (?, ?, ?, ?)", ["category", "start", "end", "amount"]))

class Bought(Table):
    def __init__(self):
        super().__init__('bought')
        self.add_field(Integer('id', autoincrement=True))
        self.add_field(Text('date'))
        self.add_field(Integer('category'))
        self.add_field(Text('name'))
        self.add_field(Integer('amount'))
        self.add_field(Integer('count'))
        #
        self.add_statement('get_sum', QuerySingle("SELECT sum(amount) as {fields} FROM {table} WHERE category=?", 
                                                         ['amount'],['category']))        
        self.add_statement('get_500', QueryMulti("SELECT {fields} FROM {table} ORDER BY date DESC LIMIT 500", 
                                                 ['id', 'date', 'category', 'name', 'amount', 'count']))        
        self.add_statement('edit', QueryUpdate("UPDATE {table} SET date=?, category=?, name=?, amount=?, count=? WHERE id=?", 
                                                 ['date', 'category', 'name', 'amount', 'count', 'id']))        
        self.add_statement('delete', QueryDelete("DELETE FROM {table} WHERE id=?", ['id']))        
        self.add_statement('add', QueryInsert("INSERT INTO {table} (date, category, name, amount, count) VALUES (?, ?, ?, ?, ?)", 
                                              ['date', 'category', 'name', 'amount', 'count']))        
        self.add_statement('get_max_id', QuerySingle("SELECT max(id) as {fields} FROM {table}", ['id']))        
